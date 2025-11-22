/**
 * LLM Provider Configuration
 * 
 * Configuration utilities for AI SDK providers.
 * Supports OpenAI, Anthropic, Google Gemini, and OpenRouter.
 */

import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import type { LanguageModel } from "ai";
import { getApiKey } from "./api-keys";
import type { ProviderType } from "./api-keys";

// Re-export ProviderType for convenience
export type { ProviderType } from "./api-keys";

export interface ProviderConfig {
  id: ProviderType;
  name: string;
  models: string[];
  defaultModel: string;
  description: string;
}

/**
 * Model cost indicators ($ = cheapest, $$$$ = most expensive)
 * Based on approximate pricing tiers as of 2024
 */
export const MODEL_COSTS: Record<string, string> = {
  // OpenAI
  "gpt-3.5-turbo": "$",
  "gpt-4": "$$$",
  "gpt-4-turbo-preview": "$$$",
  
  // Anthropic
  "claude-3-sonnet-20240229": "$$",
  "claude-3-sonnet": "$$",
  "claude-3-5-sonnet-20241022": "$$",
  "claude-3-5-sonnet": "$$",
  "claude-3-opus-20240229": "$$$$",
  "claude-3-opus": "$$$$",
  
  // Google
  "gemini-3-pro": "$$$$",
  "gemini-2.5-pro": "$$$",
  "gemini-2.5-flash": "$",
  "gemini-2.5-flash-lite": "$",
  "gemini-2.0-flash": "$",
  "gemini-2.0-flash-lite": "$",
  
  // OpenRouter (approximate based on underlying models)
  "openai/gpt-4-turbo": "$$$",
  "anthropic/claude-3-opus": "$$$$",
  "google/gemini-pro": "$",
  "mistralai/mistral-large": "$$",
  "x-ai/grok-beta": "$$",
};

/**
 * Get cost indicator for a model
 */
export function getModelCost(model: string): string {
  return MODEL_COSTS[model] || "$$";
}

export const PROVIDER_CONFIGS: Record<ProviderType, ProviderConfig> = {
  openai: {
    id: "openai",
    name: "OpenAI",
    models: ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
    defaultModel: "gpt-4-turbo-preview",
    description: "GPT-4 and GPT-3.5 models",
  },
  anthropic: {
    id: "anthropic",
    name: "Anthropic",
    models: ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-opus", "claude-3-5-sonnet", "claude-3-sonnet"],
    defaultModel: "claude-3-5-sonnet-20241022",
    description: "Claude 3.5 Sonnet and other Claude models",
  },
  google: {
    id: "google",
    name: "Google Gemini",
    models: [
      "gemini-3-pro",
      "gemini-2.5-pro",
      "gemini-2.5-flash",
      "gemini-2.5-flash-lite",
      "gemini-2.0-flash",
      "gemini-2.0-flash-lite"
    ],
    defaultModel: "gemini-3-pro",
    description: "Google's state-of-the-art Gemini models",
  },
  openrouter: {
    id: "openrouter",
    name: "OpenRouter",
    models: [
      "openai/gpt-4-turbo",
      "anthropic/claude-3-opus",
      "google/gemini-pro",
      "mistralai/mistral-large",
      "x-ai/grok-beta",
    ],
    defaultModel: "openai/gpt-4-turbo",
    description: "Access to multiple models via OpenRouter",
  },
};

/**
 * Get configured language model for a provider
 */
export async function getProviderModel(
  provider: ProviderType,
  model?: string
): Promise<LanguageModel | null> {
  const apiKey = await getApiKey(provider);
  if (!apiKey) {
    return null;
  }

  const config = PROVIDER_CONFIGS[provider];
  const modelToUse = model || config.defaultModel;

  try {
    switch (provider) {
      case "openai": {
        const client = createOpenAI({ apiKey });
        return client(modelToUse);
      }
      case "anthropic": {
        const client = createAnthropic({ apiKey });
        return client(modelToUse);
      }
      case "google": {
        const client = createGoogleGenerativeAI({ apiKey });
        return client(modelToUse);
      }
      case "openrouter": {
        // OpenRouter uses OpenAI-compatible API
        const client = createOpenAI({
          apiKey,
          baseURL: "https://openrouter.ai/api/v1",
        } as any); // OpenRouter requires custom headers but AI SDK doesn't support them directly
        return client(modelToUse);
      }
      default:
        return null;
    }
  } catch (error) {
    console.error(`Failed to create model for ${provider}:`, error);
    return null;
  }
}

/**
 * Check if a provider has a valid API key
 */
export async function isProviderAvailable(provider: ProviderType): Promise<boolean> {
  try {
    const apiKey = await getApiKey(provider);
    return apiKey !== null && apiKey.length > 0;
  } catch (error) {
    // Gracefully handle errors (e.g., corrupted keys)
    console.warn(`Error checking availability for ${provider}:`, error);
    return false;
  }
}

/**
 * Get available providers (those with API keys)
 */
export async function getAvailableProviders(): Promise<ProviderType[]> {
  const providers: ProviderType[] = [];
  const allProviders: ProviderType[] = ["openai", "anthropic", "google", "openrouter"];

  for (const provider of allProviders) {
    try {
      if (await isProviderAvailable(provider)) {
        providers.push(provider);
      }
    } catch (error) {
      // Skip providers with errors (e.g., corrupted keys)
      console.warn(`Skipping provider ${provider} due to error:`, error);
    }
  }

  return providers;
}

/**
 * Model with provider information
 */
export interface ModelInfo {
  id: string; // Unique identifier: "provider:model"
  provider: ProviderType;
  model: string;
  providerName: string;
  cost: string;
}

/**
 * Get all available models from all providers with API keys
 */
export async function getAllAvailableModels(): Promise<ModelInfo[]> {
  try {
    const availableProviders = await getAvailableProviders();
    const allModels: ModelInfo[] = [];

    for (const provider of availableProviders) {
      const config = PROVIDER_CONFIGS[provider];
      for (const model of config.models) {
        allModels.push({
          id: `${provider}:${model}`,
          provider,
          model,
          providerName: config.name,
          cost: getModelCost(model),
        });
      }
    }

    return allModels;
  } catch (error) {
    // Gracefully handle errors and return empty array if something goes wrong
    console.error("Error getting available models:", error);
    return [];
  }
}

/**
 * Parse model ID to get provider and model
 */
export function parseModelId(modelId: string): { provider: ProviderType; model: string } {
  const [provider, ...modelParts] = modelId.split(":");
  return {
    provider: provider as ProviderType,
    model: modelParts.join(":"),
  };
}

