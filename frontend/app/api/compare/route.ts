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
- Trading platform setup and account management
- Trading rules and regulations (PDT rule, etc.)

IMPORTANT: Users may refer to stocks by either their company name (e.g., "Tesla", "Apple") or stock symbol (e.g., "TSLA", "AAPL"). Treat them interchangeably:
- Tesla = TSLA
- Apple = AAPL
- Microsoft = MSFT
- Google/Alphabet = GOOGL
- Amazon = AMZN
- Meta/Facebook = META
- Netflix = NFLX
- Disney = DIS
- And other major companies

For stock price queries and market analysis questions, provide detailed, helpful answers. For general questions about trading platforms, setup, education, or rules, provide clear, informative responses without forcing a specific format.

Always use real-time data when available. Be concise, direct, and actionable.`;

// Company name to symbol mapping
const COMPANY_TO_SYMBOL: Record<string, string> = {
  'tesla': 'TSLA',
  'apple': 'AAPL',
  'microsoft': 'MSFT',
  'google': 'GOOGL',
  'alphabet': 'GOOGL',
  'amazon': 'AMZN',
  'meta': 'META',
  'facebook': 'META',
  'netflix': 'NFLX',
  'disney': 'DIS',
  'jpmorgan': 'JPM',
  'jpm': 'JPM',
  'bank of america': 'BAC',
  'bofa': 'BAC',
  'walmart': 'WMT',
  'visa': 'V',
  'mastercard': 'MA',
  'home depot': 'HD',
  'procter & gamble': 'PG',
  'pg': 'PG',
  'johnson & johnson': 'JNJ',
  'jnj': 'JNJ',
  'unitedhealth': 'UNH',
  'unh': 'UNH',
  'exxon': 'XOM',
  'chevron': 'CVX',
  'nvidia': 'NVDA',
  'spy': 'SPY',
  'spdr s&p 500': 'SPY',
  's&p 500': 'SPY',
};

// Function to normalize and find stock symbol from user input
function findStockSymbol(input: string): string | null {
  if (!input || typeof input !== 'string') {
    return null;
  }
  
  const lowerInput = input.toLowerCase();
  
  // First check direct symbol match (uppercase letters, 1-5 chars)
  const symbolMatch = input.match(/\b([A-Z]{1,5})\b/);
  if (symbolMatch && symbolMatch[1].length >= 1 && symbolMatch[1].length <= 5) {
    const potentialSymbol = symbolMatch[1].toUpperCase();
    // Verify it's a known symbol or looks like one
    if (Object.values(COMPANY_TO_SYMBOL).includes(potentialSymbol) || 
        potentialSymbol.length >= 1 && potentialSymbol.length <= 5) {
      return potentialSymbol;
    }
  }
  
  // Check company name mapping (exact matches first)
  for (const [companyName, symbol] of Object.entries(COMPANY_TO_SYMBOL)) {
    // Exact word match
    if (lowerInput === companyName || lowerInput.includes(' ' + companyName + ' ') || 
        lowerInput.startsWith(companyName + ' ') || lowerInput.endsWith(' ' + companyName)) {
      return symbol;
    }
    // Partial match
    if (lowerInput.includes(companyName)) {
      return symbol;
    }
  }
  
  // Check individual words
  const words = lowerInput.split(/\s+/);
  for (const word of words) {
    if (COMPANY_TO_SYMBOL[word]) {
      return COMPANY_TO_SYMBOL[word];
    }
  }
  
  return null;
}

// Stock price function using free Yahoo Finance API (no API key required)
async function getStockPrice(symbol: string) {
  try {
    const upperSymbol = symbol.toUpperCase();
    // Use Yahoo Finance public API endpoint
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${upperSymbol}?interval=1d&range=1d`;
    
    console.log(`[getStockPrice] Fetching real-time data for ${upperSymbol} from Yahoo Finance...`);
    
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
    
    // Get current price - prioritize regularMarketPrice, fallback to previousClose
    // During market hours: use regularMarketPrice
    // After hours: use previousClose
    let currentPrice = meta.regularMarketPrice;
    if (!currentPrice || currentPrice === 0) {
      currentPrice = meta.previousClose;
    }
    if (!currentPrice || currentPrice === 0) {
      currentPrice = meta.chartPreviousClose;
    }
    if (!currentPrice || currentPrice === 0) {
      // Try to get from quote data
      const quoteData = quote;
      if (quoteData && quoteData.close && quoteData.close.length > 0) {
        const lastClose = quoteData.close[quoteData.close.length - 1];
        if (lastClose && lastClose > 0) {
          currentPrice = lastClose;
        }
      }
    }
    
    // Validate price is reasonable (not 0 and not absurdly high)
    if (!currentPrice || currentPrice === 0) {
      throw new Error(`No valid price data found for ${upperSymbol}`);
    }
    
    // Sanity check: if price seems wrong (e.g., TSLA > 1000), use previousClose
    if (upperSymbol === 'TSLA' && currentPrice > 1000) {
      console.warn(`[getStockPrice] TSLA price ${currentPrice} seems incorrect, using previousClose ${meta.previousClose}`);
      currentPrice = meta.previousClose || meta.chartPreviousClose || currentPrice;
    }
    
    const previousClose = meta.previousClose || meta.chartPreviousClose || currentPrice;
    const change = currentPrice - previousClose;
    const changePercent = previousClose !== 0 ? (change / previousClose) * 100 : 0;
    
    // Get market time from API
    const marketTime = meta.regularMarketTime ? new Date(meta.regularMarketTime * 1000) : new Date();
    const dataTimestamp = marketTime.toISOString();
    
    // Validate we got real data
    if (!currentPrice || currentPrice === 0) {
      throw new Error(`Invalid price data received for ${upperSymbol}`);
    }
    
    console.log(`[getStockPrice] ${upperSymbol} real-time data:`, {
      price: currentPrice,
      priceSource: meta.regularMarketPrice ? 'regularMarketPrice' : (meta.previousClose ? 'previousClose' : 'chartPreviousClose'),
      change: change,
      changePercent: changePercent.toFixed(2) + '%',
      marketState: meta.marketState,
      marketTime: marketTime.toLocaleString('en-US', { timeZone: 'America/New_York' }),
      dataSource: 'Yahoo Finance API',
      rawMeta: {
        regularMarketPrice: meta.regularMarketPrice,
        previousClose: meta.previousClose,
        chartPreviousClose: meta.chartPreviousClose,
      }
    });
    
    return {
      symbol: upperSymbol,
      price: currentPrice,
      change: change,
      changePercent: changePercent,
      marketState: meta.marketState || 'UNKNOWN',
      timestamp: dataTimestamp,
      marketTime: marketTime,
      currency: meta.currency || 'USD',
      marketCap: meta.marketCap || null,
      volume: meta.regularMarketVolume || quote?.volume?.[0] || null,
      high: meta.regularMarketDayHigh || quote?.high?.[0] || null,
      low: meta.regularMarketDayLow || quote?.low?.[0] || null,
      open: meta.regularMarketOpen || quote?.open?.[0] || null,
      dataSource: 'Yahoo Finance',
      isRealTime: meta.marketState === 'REGULAR' || meta.marketState === 'PRE' || meta.marketState === 'POST',
    };
  } catch (error: any) {
    console.error(`[getStockPrice] Error fetching stock price for ${symbol}:`, error);
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

            // Check if prompt is asking for stock price or market analysis (not platform/setup questions)
            const isStockPriceQuery = /\b(price|quote|current|latest|stock|trading|symbol|ticker|how much|what.*price|summarize|analyze|support|resistance|headlines|fed|macro|options|flow|put|call|ratio|insight|bullish|bearish|tsla|spy|aapl|msft|googl|amzn|meta|nflx|dis|tesla|apple|microsoft|google|amazon|netflix|disney)\b/i.test(prompt);
            
            // Check if it's a platform/setup/education question (should NOT use template format)
            const isPlatformQuestion = /\b(how to|setup|account|robinhood|documents|pdt rule|get started|trading habits|compulsive|platform|broker|exchange)\b/i.test(prompt);
            
            // Try to find stock symbol from prompt (handles both symbols and company names)
            const foundSymbol = findStockSymbol(prompt);
            
            console.log(`[${provider}:${model}] Prompt analysis:`, {
              prompt: prompt.substring(0, 100),
              isStockPriceQuery,
              isPlatformQuestion,
              foundSymbol,
            });
            
            // If it's a stock price query (and NOT a platform question), fetch the data and use template format
            let enhancedPrompt = prompt;
            if (isStockPriceQuery && !isPlatformQuestion && foundSymbol) {
              const symbol = foundSymbol.toUpperCase();
              console.log(`[${provider}:${model}] Detected stock query for ${symbol}, fetching price and using template format...`);
              try {
                const priceData = await getStockPrice(symbol);
                if (priceData.error) {
                  enhancedPrompt = `${prompt}\n\nNote: I encountered an error fetching the stock price: ${priceData.error}`;
                } else {
                  const currentTime = new Date().toLocaleTimeString('en-US', { 
                    timeZone: 'America/New_York', 
                    hour: 'numeric', 
                    minute: '2-digit',
                    hour12: true 
                  }) + ' ET';
                  
                  const price = (priceData.price || 0).toFixed(2);
                  const change = (priceData.change || 0);
                  const changePercent = (priceData.changePercent || 0);
                  const high = priceData.high || priceData.price || 0;
                  const low = priceData.low || priceData.price || 0;
                  const range = `$${low.toFixed(2)}-$${high.toFixed(2)}`;
                  const resistance = high.toFixed(2);
                  const momentum = change >= 0 ? 'bulls' : 'bears';
                  const volatility = Math.abs(changePercent) > 3 ? 'high' : Math.abs(changePercent) > 1.5 ? 'moderate' : 'low';
                  
                  // Use market time from API if available, otherwise use current time
                  const displayTime = priceData.marketTime 
                    ? priceData.marketTime.toLocaleTimeString('en-US', { 
                        timeZone: 'America/New_York', 
                        hour: 'numeric', 
                        minute: '2-digit',
                        hour12: true 
                      }) + ' ET'
                    : currentTime;
                  
                  const dataSourceNote = priceData.isRealTime 
                    ? ' (Real-time data from Yahoo Finance)'
                    : ' (Market data from Yahoo Finance)';
                  
                  // CRITICAL: Use EXACT price values from API - do not let model invent numbers
                  // Use template format ONLY for stock queries
                  enhancedPrompt = `${prompt}\n\nIMPORTANT: Use ONLY the exact market data provided below. Do NOT invent or estimate prices.\n\nCurrent market data for ${symbol}${dataSourceNote}:\n` +
                    `- Price: $${price} (EXACT - use this exact value)\n` +
                    `- Time: ${displayTime}\n` +
                    `- Change: ${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)\n` +
                    `- Range: ${range}\n` +
                    `- Resistance: $${resistance}\n` +
                    `- High: $${high.toFixed(2)}\n` +
                    `- Low: $${low.toFixed(2)}\n` +
                    `- Volume: ${priceData.volume ? priceData.volume.toLocaleString() : 'N/A'}\n` +
                    `- Market State: ${priceData.marketState || 'UNKNOWN'}\n` +
                    `- Data Source: Yahoo Finance API (verified real-time)\n\n` +
                    `CRITICAL INSTRUCTIONS:\n` +
                    `1. Use EXACTLY $${price} as the price - do not change this number\n` +
                    `2. Use EXACTLY ${displayTime} as the time\n` +
                    `3. Use EXACTLY $${resistance} as the resistance level\n` +
                    `4. Use EXACTLY ${range} as the range\n` +
                    `5. Format your response EXACTLY as: "${symbol} $${price} at ${displayTime}, testing resistance near $${resistance} (${range}). Momentum favors ${momentum}, but volatility remains ${volatility}; next catalysts include {relevant catalysts based on the stock}."\n` +
                    `6. Do NOT invent or estimate any price values - use only the exact numbers provided above.`;
                }
              } catch (e) {
                console.error(`[${provider}:${model}] Error fetching stock price:`, e);
              }
            } else if (isStockPriceQuery && !isPlatformQuestion && !foundSymbol) {
              // Stock query but no symbol found - still try to help but don't force template
              console.log(`[${provider}:${model}] Stock query detected but no symbol found, answering normally`);
            } else {
              // Platform/setup/education questions - answer normally without template format
              console.log(`[${provider}:${model}] Non-stock query detected, answering normally without template format`);
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

        // generateText should return text response
        let responseText = result.text || "";
        
        // If no text but we have tool results, log them for debugging
        if (!responseText && result.toolResults && result.toolResults.length > 0) {
          console.log(`[${provider}:${model}] No text but have tool results:`, JSON.stringify(result.toolResults, null, 2));
        }
        
        // If still no text, check finish reason
        if (!responseText) {
          console.error(`[${provider}:${model}] No text content generated. Result:`, JSON.stringify({
            toolCalls: result.toolCalls,
            toolResults: result.toolResults,
            finishReason: result.finishReason,
            hasText: !!result.text,
            text: result.text,
          }, null, 2));
          
          // Return error if no text is generated
          return {
            modelId,
            provider,
            model: model,
            content: "",
            error: `No response generated. Finish reason: ${result.finishReason || 'unknown'}. The model may have encountered an issue processing your request.`,
            completed: false,
          };
        }
        
        console.log(`[${provider}:${model}] Successfully generated response (${responseText.length} chars)`);

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

