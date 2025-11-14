import { NextRequest, NextResponse } from "next/server";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import type { ProviderType } from "@/lib/api-keys";

const SYSTEM_PROMPT = "Be concise and direct. Get straight to the point. Use short paragraphs, bullet points, and clear formatting. No fluff—save time with actionable answers.";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, providers, models, apiKeys, modelIds } = body;

    if (!prompt) {
      return NextResponse.json(
        { error: "Invalid request. Prompt is required." },
        { status: 400 }
      );
    }

    if (!apiKeys || typeof apiKeys !== "object") {
      return NextResponse.json(
        { error: "API keys are required." },
        { status: 400 }
      );
    }

    // Build model requests from modelIds if provided, otherwise use providers/models
    interface ModelRequest {
      modelId: string;
      provider: ProviderType;
      model: string;
    }

    const modelRequests: ModelRequest[] = [];
    
    if (modelIds && Array.isArray(modelIds) && modelIds.length > 0) {
      // Use modelIds for individual model selection
      modelIds.forEach((modelId: string) => {
        const [provider, ...modelParts] = modelId.split(":");
        const model = modelParts.join(":");
        modelRequests.push({
          modelId,
          provider: provider as ProviderType,
          model,
        });
      });
    } else if (providers && Array.isArray(providers) && providers.length > 0) {
      // Fallback to provider-based selection
      providers.forEach((provider: ProviderType) => {
        const model = models?.[provider] || getDefaultModel(provider);
        modelRequests.push({
          modelId: `${provider}:${model}`,
          provider,
          model,
        });
      });
    } else {
      return NextResponse.json(
        { error: "Invalid request. Providers or modelIds are required." },
        { status: 400 }
      );
    }

    // Make parallel API calls
    const promises = modelRequests.map(async ({ modelId, provider, model }) => {
      try {
        const apiKey = apiKeys[provider];
        if (!apiKey) {
          throw new Error(`No API key provided for ${provider}`);
        }

        const model = models?.[provider] || getDefaultModel(provider);
        let languageModel;

        switch (provider) {
          case "openai": {
            const client = createOpenAI({ apiKey });
            languageModel = client(model);
            break;
          }
          case "anthropic": {
            const client = createAnthropic({ apiKey });
            languageModel = client(model);
            break;
          }
          case "google": {
            const client = createGoogleGenerativeAI({ apiKey });
            languageModel = client(model);
            break;
          }
          case "openrouter": {
            const client = createOpenAI({
              apiKey,
              baseURL: "https://openrouter.ai/api/v1",
            } as any);
            languageModel = client(model);
            break;
          }
          default:
            throw new Error(`Unsupported provider: ${provider}`);
        }

        const result = await generateText({
          model: languageModel,
          system: SYSTEM_PROMPT,
          prompt,
        });

        return {
          modelId,
          provider,
          model,
          content: result.text,
          error: null,
          completed: true,
        };
      } catch (error: any) {
        let errorMessage = "Unknown error occurred";

        if (error instanceof Error) {
          errorMessage = error.message;
          // Provide more helpful error messages
          if (errorMessage.includes("401") || errorMessage.includes("Unauthorized") || errorMessage.includes("authentication")) {
            errorMessage = "Invalid API key. Please check your API key in Settings.";
          } else if (errorMessage.includes("429") || errorMessage.includes("rate limit")) {
            errorMessage = "Rate limit exceeded. Please try again later.";
          } else if (errorMessage.includes("404") || errorMessage.includes("Not Found") || errorMessage.includes("model_not_found")) {
            errorMessage = `Model "${model}" may not be available or your API key doesn't have access to it.`;
          } else if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError") || errorMessage.includes("network")) {
            errorMessage = "Network error. This could be a CORS issue or network connectivity problem. Check your API key and internet connection.";
          } else if (errorMessage.includes("403") || errorMessage.includes("Forbidden")) {
            errorMessage = "Access forbidden. Your API key may not have access to this model or feature.";
          } else if (errorMessage.includes("400") || errorMessage.includes("Bad Request")) {
            errorMessage = `Invalid request. The model "${model}" may not be supported or the request format is incorrect.`;
          }
        }

        return {
          modelId,
          provider,
          model,
          content: "",
          error: errorMessage,
          completed: false,
        };
      }
    });

    const results = await Promise.allSettled(promises);
    const responses = results.map((result) => {
      if (result.status === "fulfilled") {
        return result.value;
      } else {
        return {
          provider: "unknown" as ProviderType,
          model: "unknown",
          content: "",
          error: result.reason?.message || "Unknown error occurred",
          completed: false,
        };
      }
    });

    return NextResponse.json({ responses });
  } catch (error: any) {
    console.error("Error in compare API route:", error);
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
}

function getDefaultModel(provider: ProviderType): string {
  const defaults: Record<ProviderType, string> = {
    openai: "gpt-4-turbo-preview",
    anthropic: "claude-3-5-sonnet-20241022",
    google: "gemini-1.5-pro",
    openrouter: "openai/gpt-4-turbo",
  };
  return defaults[provider] || "";
}

