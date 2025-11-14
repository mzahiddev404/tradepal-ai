import { NextRequest, NextResponse } from "next/server";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { createAnthropic } from "@ai-sdk/anthropic";
import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { z } from "zod";
import { zodSchema } from "ai";
import type { ProviderType } from "@/lib/api-keys";

const SYSTEM_PROMPT = `You are a stock market and investing AI assistant. Your expertise includes:
- Stock market analysis and trading strategies
- Options trading (calls, puts, spreads)
- Market trends and technical analysis
- Risk assessment and portfolio management
- Investment education and best practices

When users ask about stock prices or market data, use the get_stock_price function to fetch current data.
Always use real-time data when available. Be concise, direct, and actionable.`;

// Stock price function using free Yahoo Finance API (no API key required)
async function getStockPrice(symbol: string) {
  try {
    const upperSymbol = symbol.toUpperCase();
    // Use Yahoo Finance public API endpoint
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${upperSymbol}?interval=1d&range=1d`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.chart || !data.chart.result || data.chart.result.length === 0) {
      throw new Error(`No data found for symbol ${upperSymbol}`);
    }

    const result = data.chart.result[0];
    const meta = result.meta;
    const quote = result.indicators?.quote?.[0];
    
    // Get current price (use regularMarketPrice or last close)
    const currentPrice = meta.regularMarketPrice || meta.previousClose || 0;
    const previousClose = meta.previousClose || currentPrice;
    const change = currentPrice - previousClose;
    const changePercent = previousClose !== 0 ? (change / previousClose) * 100 : 0;
    
    return {
      symbol: upperSymbol,
      price: currentPrice,
      change: change,
      changePercent: changePercent,
      marketState: meta.marketState || 'UNKNOWN',
      timestamp: new Date().toISOString(),
      currency: meta.currency || 'USD',
      marketCap: meta.marketCap || null,
      volume: meta.regularMarketVolume || quote?.volume?.[0] || null,
      high: meta.regularMarketDayHigh || quote?.high?.[0] || null,
      low: meta.regularMarketDayLow || quote?.low?.[0] || null,
      open: meta.regularMarketOpen || quote?.open?.[0] || null,
    };
  } catch (error: any) {
    console.error(`Error fetching stock price for ${symbol}:`, error);
    return { 
      error: `Failed to fetch price for ${symbol.toUpperCase()}. ${error.message || 'Please check the symbol is correct.'}`,
      symbol: symbol.toUpperCase()
    };
  }
}

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
    const promises = modelRequests.map(async ({ modelId, provider, model: modelName }) => {
      try {
        const apiKey = apiKeys[provider];
        if (!apiKey) {
          throw new Error(`No API key provided for ${provider}`);
        }

        const model = modelName || models?.[provider] || getDefaultModel(provider);
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

        // Define tool schema
        const stockPriceSchema = z.object({
          symbol: z.string().describe("Stock ticker symbol (e.g., TSLA, AAPL, SPY, MSFT)")
        });

        // Check if prompt is asking for stock price
        const stockSymbolMatch = prompt.match(/\b(TSLA|AAPL|SPY|MSFT|NVDA|GOOGL|AMZN|META|NFLX|DIS|JPM|BAC|WMT|V|MA|HD|PG|JNJ|UNH|XOM|CVX)\b/i);
        const isStockPriceQuery = /\b(price|quote|current|latest|stock|trading|symbol|ticker|how much|what.*price)\b/i.test(prompt);
        
        // If it's a stock price query, fetch the data first and include it in the prompt
        let enhancedPrompt = prompt;
        if (isStockPriceQuery && stockSymbolMatch) {
          const symbol = stockSymbolMatch[1].toUpperCase();
          console.log(`[${provider}:${model}] Detected stock query for ${symbol}, fetching price...`);
          try {
            const priceData = await getStockPrice(symbol);
            if (priceData.error) {
              enhancedPrompt = `${prompt}\n\nNote: I encountered an error fetching the stock price: ${priceData.error}`;
            } else {
              const changeSign = (priceData.change || 0) >= 0 ? '+' : '';
              const percentSign = (priceData.changePercent || 0) >= 0 ? '+' : '';
              const priceStr = (priceData.price || 0).toFixed(2);
              const changeStr = (priceData.change || 0).toFixed(2);
              const percentStr = (priceData.changePercent || 0).toFixed(2);
              const volumeStr = priceData.volume ? priceData.volume.toLocaleString() : 'N/A';
              const highStr = priceData.high ? '$' + priceData.high.toFixed(2) : 'N/A';
              const lowStr = priceData.low ? '$' + priceData.low.toFixed(2) : 'N/A';
              
              enhancedPrompt = prompt + '\n\nCurrent market data for ' + symbol + ':\n' +
                '- Price: $' + priceStr + '\n' +
                '- Change: ' + changeSign + changeStr + ' (' + percentSign + percentStr + '%)\n' +
                '- Market State: ' + (priceData.marketState || 'UNKNOWN') + '\n' +
                '- Volume: ' + volumeStr + '\n' +
                '- High: ' + highStr + '\n' +
                '- Low: ' + lowStr;
            }
          } catch (e) {
            console.error(`[${provider}:${model}] Error fetching stock price:`, e);
          }
        }

        const result = await generateText({
          model: languageModel,
          system: SYSTEM_PROMPT,
          prompt: enhancedPrompt,
        });

        // Log full result for debugging
        console.log(`[${provider}:${model}] Full result:`, {
          hasText: !!result.text,
          textLength: result.text?.length || 0,
          textPreview: result.text?.substring(0, 200) || "NO TEXT",
          toolCalls: result.toolCalls?.length || 0,
          toolResults: result.toolResults?.length || 0,
          finishReason: result.finishReason,
          usage: result.usage,
          fullResultKeys: Object.keys(result),
        });

        // generateText with tools should automatically handle tool execution and return final text
        // If result.text is empty, check if we have tool calls/results
        let responseText = result.text || "";
        
        // If no text but we have tool results, log them for debugging
        if (!responseText && result.toolResults && result.toolResults.length > 0) {
          console.log(`[${provider}:${model}] No text but have tool results:`, JSON.stringify(result.toolResults, null, 2));
        }
        
        if (!responseText) {
          console.error(`[${provider}:${model}] No text content generated. Result:`, JSON.stringify({
            toolCalls: result.toolCalls,
            toolResults: result.toolResults,
            finishReason: result.finishReason,
            hasText: !!result.text,
          }, null, 2));
          
          // Return error if no text is generated
          return {
            modelId,
            provider,
            model: model,
            content: "",
            error: "No response generated. The model may have encountered an issue processing your request. Check server logs for details.",
            completed: false,
          };
        }

        return {
          modelId,
          provider,
          model: model,
          content: responseText,
          error: null,
          completed: true,
        };
      } catch (error: any) {
        let errorMessage = "Unknown error occurred";
        const modelForError = modelName || models?.[provider] || getDefaultModel(provider);

        if (error instanceof Error) {
          errorMessage = error.message;
          // Provide more helpful error messages
          if (errorMessage.includes("401") || errorMessage.includes("Unauthorized") || errorMessage.includes("authentication")) {
            errorMessage = "Invalid API key. Please check your API key in Settings.";
          } else if (errorMessage.includes("429") || errorMessage.includes("rate limit")) {
            errorMessage = "Rate limit exceeded. Please try again later.";
          } else if (errorMessage.includes("404") || errorMessage.includes("Not Found") || errorMessage.includes("model_not_found")) {
            errorMessage = `Model "${modelForError}" may not be available or your API key doesn't have access to it.`;
          } else if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError") || errorMessage.includes("network")) {
            errorMessage = "Network error. This could be a CORS issue or network connectivity problem. Check your API key and internet connection.";
          } else if (errorMessage.includes("403") || errorMessage.includes("Forbidden")) {
            errorMessage = "Access forbidden. Your API key may not have access to this model or feature.";
          } else if (errorMessage.includes("400") || errorMessage.includes("Bad Request")) {
            errorMessage = `Invalid request. The model "${modelForError}" may not be supported or the request format is incorrect.`;
          }
        }

        return {
          modelId,
          provider,
          model: modelForError,
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

