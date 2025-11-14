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
  modelId: string; // "provider:model" format
  content: string;
  error?: string;
  isLoading: boolean;
  completed: boolean;
}

export interface UseMultiLLMReturn {
  responses: Record<string, LLMResponse | null>; // Keyed by modelId
  isLoading: boolean;
  sendMessage: (prompt: string, providers: ProviderType[], models?: Record<ProviderType, string>, modelIds?: string[]) => Promise<void>;
  clearResponses: () => void;
  error: string | null;
}

export function useMultiLLM(): UseMultiLLMReturn {
  const [responses, setResponses] = useState<Record<string, LLMResponse | null>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (
      prompt: string,
      providers: ProviderType[],
      models?: Record<ProviderType, string>,
      modelIds?: string[]
    ) => {
      if (!prompt.trim() || providers.length === 0) {
        return;
      }

      setError(null);
      setIsLoading(true);

      // Initialize responses using modelIds if provided, otherwise use providers
      const initialResponses: Record<string, LLMResponse | null> = {};
      
      if (modelIds && modelIds.length > 0) {
        // Use modelIds for individual model tracking
        modelIds.forEach((modelId) => {
          const { provider, model } = modelId.includes(":") 
            ? { provider: modelId.split(":")[0] as ProviderType, model: modelId.split(":").slice(1).join(":") }
            : { provider: providers[0], model: models?.[providers[0]] || PROVIDER_CONFIGS[providers[0]].defaultModel };
          
          initialResponses[modelId] = {
            provider,
            model,
            modelId,
            content: "",
            isLoading: true,
            completed: false,
          };
        });
      } else {
        // Fallback to provider-based tracking
        providers.forEach((provider) => {
          const config = PROVIDER_CONFIGS[provider];
          const model = models?.[provider] || config.defaultModel;
          const modelId = `${provider}:${model}`;
          initialResponses[modelId] = {
            provider,
            model,
            modelId,
            content: "",
            isLoading: true,
            completed: false,
          };
        });
      }
      
      setResponses(initialResponses);

      // Collect API keys for selected providers
      const apiKeys: Record<ProviderType, string> = {} as Record<ProviderType, string>;
      for (const provider of providers) {
        const apiKey = await getApiKey(provider);
        if (!apiKey) {
          // Mark all models from this provider as failed
          const failedModelIds = modelIds 
            ? modelIds.filter(id => id.startsWith(`${provider}:`))
            : [`${provider}:${models?.[provider] || PROVIDER_CONFIGS[provider].defaultModel}`];
          
          failedModelIds.forEach((modelId) => {
            setResponses((prev) => ({
              ...prev,
              [modelId]: {
                provider,
                model: modelId.split(":").slice(1).join(":"),
                modelId,
                content: "",
                error: `No API key configured for ${PROVIDER_CONFIGS[provider].name}. Please add it in Settings.`,
                isLoading: false,
                completed: false,
              },
            }));
          });
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
            modelIds,
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
            const modelId = result.modelId || `${result.provider}:${result.model}`;
            setResponses((prev) => ({
              ...prev,
              [modelId]: {
                provider: result.provider,
                model: result.model,
                modelId,
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
        
        // Mark all models as failed
        const failedModelIds = modelIds || providers.map(p => `${p}:${models?.[p] || PROVIDER_CONFIGS[p].defaultModel}`);
        failedModelIds.forEach((modelId) => {
          const { provider, model } = modelId.includes(":")
            ? { provider: modelId.split(":")[0] as ProviderType, model: modelId.split(":").slice(1).join(":") }
            : { provider: providers[0], model: models?.[providers[0]] || PROVIDER_CONFIGS[providers[0]].defaultModel };
          
          setResponses((prev) => ({
            ...prev,
            [modelId]: {
              provider,
              model,
              modelId,
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
    setResponses({});
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

