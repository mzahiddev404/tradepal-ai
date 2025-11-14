/**
 * useMultiLLM Hook
 * 
 * Custom hook for managing multi-LLM comparison functionality.
 * Handles parallel API calls to multiple LLM providers via Next.js API route.
 */

import { useState, useCallback } from "react";
import { PROVIDER_CONFIGS, type ProviderType } from "@/lib/llm-providers";
import { getApiKey } from "@/lib/api-keys";

export interface LLMResponse {
  provider: ProviderType;
  model: string;
  content: string;
  error?: string;
  isLoading: boolean;
  completed: boolean;
}

export interface UseMultiLLMReturn {
  responses: Record<ProviderType, LLMResponse | null>;
  isLoading: boolean;
  sendMessage: (prompt: string, providers: ProviderType[], models?: Record<ProviderType, string>) => Promise<void>;
  clearResponses: () => void;
  error: string | null;
}

export function useMultiLLM(): UseMultiLLMReturn {
  const [responses, setResponses] = useState<Record<ProviderType, LLMResponse | null>>({} as Record<ProviderType, LLMResponse | null>);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (
      prompt: string,
      providers: ProviderType[],
      models?: Record<ProviderType, string>
    ) => {
      if (!prompt.trim() || providers.length === 0) {
        return;
      }

      setError(null);
      setIsLoading(true);

      // Initialize responses
      const initialResponses: Record<ProviderType, LLMResponse | null> = {} as Record<ProviderType, LLMResponse | null>;
      providers.forEach((provider) => {
        const config = PROVIDER_CONFIGS[provider];
        const model = models?.[provider] || config.defaultModel;
        initialResponses[provider] = {
          provider,
          model,
          content: "",
          isLoading: true,
          completed: false,
        };
      });
      setResponses(initialResponses);

      // Collect API keys for selected providers
      const apiKeys: Record<ProviderType, string> = {} as Record<ProviderType, string>;
      for (const provider of providers) {
        const apiKey = await getApiKey(provider);
        if (!apiKey) {
          setResponses((prev) => ({
            ...prev,
            [provider]: {
              provider,
              model: models?.[provider] || PROVIDER_CONFIGS[provider].defaultModel,
              content: "",
              error: `No API key configured for ${PROVIDER_CONFIGS[provider].name}. Please add it in Settings.`,
              isLoading: false,
              completed: false,
            },
          }));
          setIsLoading(false);
          return;
        }
        apiKeys[provider] = apiKey;
      }

      // Make API call to Next.js route
      try {
        const response = await fetch("/api/compare", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt,
            providers,
            models,
            apiKeys,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ error: "Unknown error" }));
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Update responses from API
        if (data.responses && Array.isArray(data.responses)) {
          data.responses.forEach((result: any) => {
            setResponses((prev) => ({
              ...prev,
              [result.provider]: {
                provider: result.provider,
                model: result.model,
                content: result.content || "",
                error: result.error || undefined,
                isLoading: false,
                completed: result.completed || false,
              },
            }));
          });
        }
      } catch (err) {
        console.error("Error calling compare API:", err);
        const errorMessage = err instanceof Error ? err.message : "Failed to generate responses";
        setError(errorMessage);
        
        // Mark all providers as failed
        providers.forEach((provider) => {
          setResponses((prev) => ({
            ...prev,
            [provider]: {
              provider,
              model: models?.[provider] || PROVIDER_CONFIGS[provider].defaultModel,
              content: "",
              error: errorMessage,
              isLoading: false,
              completed: false,
            },
          }));
        });
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const clearResponses = useCallback(() => {
    setResponses({} as Record<ProviderType, LLMResponse | null>);
    setError(null);
  }, []);

  return {
    responses,
    isLoading,
    sendMessage,
    clearResponses,
    error,
  };
}

