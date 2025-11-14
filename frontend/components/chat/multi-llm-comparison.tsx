"use client";

/**
 * Multi-LLM Comparison Component
 * 
 * Displays side-by-side comparison of responses from multiple LLM providers.
 */

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChatInput } from "./chat-input";
import { ModelSelector } from "./model-selector";
import { useMultiLLM } from "@/hooks/useMultiLLM";
import { PROVIDER_CONFIGS, getModelCost, type ProviderType } from "@/lib/llm-providers";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Spinner } from "@/components/ui/spinner";
import { AlertCircle, CheckCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { CHAT_SUGGESTIONS } from "@/constants/chat";

export function MultiLLMComparison() {
  const [selectedProviders, setSelectedProviders] = useState<ProviderType[]>([]);
  const [selectedModels, setSelectedModels] = useState<Record<ProviderType, string>>({} as Record<ProviderType, string>);
  const [showSelector, setShowSelector] = useState(true);
  const [expandedResponses, setExpandedResponses] = useState<Record<ProviderType, boolean>>({} as Record<ProviderType, boolean>);
  const { responses, isLoading, sendMessage, clearResponses, error } = useMultiLLM();

  const handleSend = (prompt: string) => {
    if (selectedProviders.length === 0) {
      return;
    }
    setShowSelector(false);
    sendMessage(prompt, selectedProviders, selectedModels);
  };


  const handleClear = () => {
    clearResponses();
    setShowSelector(true);
    setExpandedResponses({} as Record<ProviderType, boolean>);
  };

  const hasResponses = Object.values(responses).some((r) => r !== null);
  const allResponsesCompleted = selectedProviders.every(
    (provider) => responses[provider]?.completed || responses[provider]?.error
  );
  // Show suggestions when providers are selected (ready to chat) or after responses complete
  const showSuggestions = selectedProviders.length > 0 && (!showSelector || allResponsesCompleted);

  const toggleExpand = (provider: ProviderType) => {
    setExpandedResponses((prev) => ({
      ...prev,
      [provider]: !prev[provider],
    }));
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
  };

  const MAX_PREVIEW_LENGTH = 500;

  return (
    <div className="flex flex-col h-full">
      {showSelector && (
        <>
          <div className="p-4 border-b border-[#2d3237]">
            <ModelSelector
              selectedProviders={selectedProviders}
              selectedModels={selectedModels}
              onProvidersChange={setSelectedProviders}
              onModelsChange={setSelectedModels}
            />
          </div>
          {selectedProviders.length > 0 && (
            <div className="px-4 pb-4 border-b border-[#2d3237] pt-4 space-y-3">
              <p className="text-xs font-semibold text-[#34c759] uppercase tracking-wider flex items-center gap-2">
                <span className="h-1 w-1 rounded-full bg-[#34c759]"></span>
                Try These Prompts
              </p>
              <div className="flex flex-wrap gap-2">
                {CHAT_SUGGESTIONS.slice(0, 4).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                    disabled={isLoading}
                    className="px-3 py-2 text-xs sm:text-sm rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap font-medium"
                  >
                    {suggestion.text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {!showSelector && (
        <div className="flex-1 overflow-hidden flex flex-col">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {selectedProviders.map((provider) => {
                const response = responses[provider];
                const config = PROVIDER_CONFIGS[provider];
                const model = selectedModels[provider] || config.defaultModel;

                return (
                  <Card
                    key={provider}
                    className={cn(
                      "border-[#2d3237] bg-[#1a1e23]/95",
                      response?.error && "border-[#ff3b30]",
                      response?.completed && !response.error && "border-[#34c759]"
                    )}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-[#dcdcdc] text-lg">
                            {config.name}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <p className="text-xs text-[#9ca3af]">{model}</p>
                            <span className="text-xs text-[#9ca3af]">•</span>
                            <span className="text-xs text-[#9ca3af]">{getModelCost(model)}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {response?.isLoading && (
                            <Spinner className="h-4 w-4 text-[#34c759]" />
                          )}
                          {response?.error && (
                            <XCircle className="h-4 w-4 text-[#ff3b30]" />
                          )}
                          {response?.completed && !response.error && (
                            <CheckCircle className="h-4 w-4 text-[#34c759]" />
                          )}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      {response?.isLoading && !response.content && (
                        <div className="flex items-center gap-2 text-[#9ca3af]">
                          <Spinner className="h-4 w-4" />
                          <span className="text-sm">Generating response...</span>
                        </div>
                      )}
                      {response?.error && (
                        <div className="rounded-lg border border-[#ff3b30] bg-[#2d1f1f] p-3">
                          <div className="flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-[#ff3b30] mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <p className="text-sm text-[#ff6b6b]">{response.error}</p>
                              {response.error.includes("Network error") && (
                                <p className="text-xs text-[#9ca3af] mt-2">
                                  Tip: Check browser console (F12) for details. Claude 3 Opus may require a premium API tier. Try Claude 3.5 Sonnet instead.
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                      {response?.content && (
                        <div className="prose prose-invert max-w-none">
                          <p className="text-[#dcdcdc] whitespace-pre-wrap leading-relaxed">
                            {expandedResponses[provider] || response.content.length <= MAX_PREVIEW_LENGTH
                              ? response.content
                              : `${response.content.slice(0, MAX_PREVIEW_LENGTH)}...`}
                          </p>
                          {response.content.length > MAX_PREVIEW_LENGTH && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleExpand(provider)}
                              className="mt-2 text-[#34c759] hover:text-[#34c759] hover:bg-[#1a2e1a]/30"
                            >
                              {expandedResponses[provider] ? "Show Less" : "Show More"}
                            </Button>
                          )}
                        </div>
                      )}
                      {!response && !isLoading && (
                        <p className="text-[#9ca3af] text-sm">Waiting for response...</p>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
            {!hasResponses && !isLoading && (
              <div className="flex items-center justify-center h-full min-h-[200px]">
                <div className="text-center space-y-4">
                  <p className="text-[#9ca3af] text-sm">
                    Ready to compare. Send a message below or use the suggestions.
                  </p>
                </div>
              </div>
            )}
          </ScrollArea>
          {showSuggestions && (
            <div className="px-4 pb-4 border-t border-[#2d3237] pt-4 space-y-3">
              <p className="text-xs font-semibold text-[#34c759] uppercase tracking-wider flex items-center gap-2">
                <span className="h-1 w-1 rounded-full bg-[#34c759]"></span>
                Try These Prompts
              </p>
              <div className="flex flex-wrap gap-2">
                {CHAT_SUGGESTIONS.slice(0, 4).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion.text)}
                    disabled={isLoading}
                    className="px-3 py-2 text-xs sm:text-sm rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap font-medium"
                  >
                    {suggestion.text}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mx-4 mb-4 rounded-lg border border-[#ff3b30] bg-[#2d1f1f] p-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-[#ff3b30] mt-0.5 flex-shrink-0" />
            <p className="text-sm text-[#ff6b6b]">{error}</p>
          </div>
        </div>
      )}

      <div className="border-t border-[#2d3237] bg-[#1a1e23]/95 p-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <ChatInput
              onSend={handleSend}
              disabled={isLoading || selectedProviders.length === 0}
            />
          </div>
          {hasResponses && (
            <Button
              variant="outline"
              onClick={handleClear}
              className="border-[#2d3237] text-[#dcdcdc] hover:bg-[#32363a]"
            >
              Clear
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

