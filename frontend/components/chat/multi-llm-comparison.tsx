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
import { PROVIDER_CONFIGS, getModelCost, parseModelId, getAllAvailableModels, type ProviderType, type ModelInfo } from "@/lib/llm-providers";
import { Spinner } from "@/components/ui/spinner";
import { AlertCircle, CheckCircle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { CHAT_SUGGESTIONS } from "@/constants/chat";
import ReactMarkdown from "react-markdown";

export function MultiLLMComparison() {
      const [selectedModelIds, setSelectedModelIds] = useState<string[]>([]);
      const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
      const [showSelector, setShowSelector] = useState(true);
      const [expandedResponses, setExpandedResponses] = useState<Record<string, boolean>>({});
      const [showPrompts, setShowPrompts] = useState(true);
      const [expandedCategory, setExpandedCategory] = useState<string | null>(null);
      const { responses, isLoading, sendMessage, clearResponses, error } = useMultiLLM();

  useEffect(() => {
    getAllAvailableModels().then(setAvailableModels);
  }, []);

  const handleSend = (prompt: string) => {
    if (selectedModelIds.length === 0) {
      return;
    }
    setShowSelector(false);
    
    // Convert model IDs to providers and models format
    const providers: ProviderType[] = [];
    const models: Record<ProviderType, string> = {} as Record<ProviderType, string>;
    
    selectedModelIds.forEach((modelId) => {
      const { provider, model } = parseModelId(modelId);
      if (!providers.includes(provider)) {
        providers.push(provider);
      }
      models[provider] = model;
    });
    
    sendMessage(prompt, providers, models, selectedModelIds);
  };

  const handleClear = () => {
    clearResponses();
    setShowSelector(true);
    setExpandedResponses({});
  };

  const hasResponses = Object.values(responses).some((r) => r !== null);
  const allResponsesCompleted = selectedModelIds.every(
    (modelId) => {
      return responses[modelId]?.completed || responses[modelId]?.error;
    }
  );
  // Show suggestions when models are selected (ready to chat) or after responses complete
  const showSuggestions = selectedModelIds.length > 0 && (!showSelector || allResponsesCompleted);

  const toggleExpand = (modelId: string) => {
    setExpandedResponses((prev) => ({
      ...prev,
      [modelId]: !prev[modelId],
    }));
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
    // Collapse all categories after selection
    setExpandedCategory(null);
  };

  const MAX_PREVIEW_LENGTH = 500;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {showSelector && (
        <>
          <div className="p-4 border-b border-[#2d3237]">
            <ModelSelector
              selectedModelIds={selectedModelIds}
              onModelsChange={setSelectedModelIds}
            />
          </div>
          {selectedModelIds.length > 0 && (
            <div className="px-4 pb-2 border-b border-[#2d3237] bg-gradient-to-b from-[#1a1e23] to-[#141820]">
              <div className="w-full flex items-center py-2">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-[#34c759] animate-pulse"></div>
                  <p className="text-xs font-bold text-[#34c759] uppercase tracking-widest">
                    Try These Prompts
                  </p>
                </div>
              </div>
              
              <div className="pb-3 space-y-3">
                  {/* Market & Analysis (combined stock prices and analysis) */}
                  <div className="space-y-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedCategory(expandedCategory === "market" ? null : "market");
                      }}
                      className="flex items-center justify-between w-full text-left px-2 py-1.5 rounded-md hover:bg-[#23272c] transition-colors cursor-pointer"
                    >
                      <p className="text-xs font-semibold text-[#9ca3af] uppercase tracking-wide">Market & Analysis</p>
                      {expandedCategory === "market" ? (
                        <ChevronUp className="h-3 w-3 text-[#9ca3af]" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-[#9ca3af]" />
                      )}
                    </button>
                    {expandedCategory === "market" && (
                      <div className="flex flex-wrap gap-1.5">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "market").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-2.5 py-1.5 text-xs rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                          >
                            {suggestion.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Setup & Education */}
                  <div className="space-y-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedCategory(expandedCategory === "setup" ? null : "setup");
                      }}
                      className="flex items-center justify-between w-full text-left px-2 py-1.5 rounded-md hover:bg-[#23272c] transition-colors cursor-pointer"
                    >
                      <p className="text-xs font-semibold text-[#9ca3af] uppercase tracking-wide">Setup & Education</p>
                      {expandedCategory === "setup" ? (
                        <ChevronUp className="h-3 w-3 text-[#9ca3af]" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-[#9ca3af]" />
                      )}
                    </button>
                    {expandedCategory === "setup" && (
                      <div className="flex flex-wrap gap-1.5">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "setup").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-2.5 py-1.5 text-xs rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                          >
                            {suggestion.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
            </div>
          )}
        </>
      )}

      {!showSelector && (
        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {selectedModelIds.map((modelId) => {
                const modelInfo = availableModels.find((m) => m.id === modelId);
                if (!modelInfo) return null;
                
                const response = responses[modelId];
                
                // Debug logging
                if (response) {
                  console.log(`[${modelId}] Response state:`, {
                    hasContent: !!response.content,
                    contentLength: response.content?.length || 0,
                    isLoading: response.isLoading,
                    completed: response.completed,
                    hasError: !!response.error,
                  });
                }

                return (
                  <Card
                    key={modelId}
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
                            {modelInfo.providerName}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <p className="text-xs text-[#9ca3af]">{modelInfo.model}</p>
                            <span className="text-xs text-[#9ca3af]">•</span>
                            <span className="text-xs text-[#9ca3af]">{modelInfo.cost}</span>
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
                          <div className="text-[#dcdcdc] leading-relaxed">
                            <ReactMarkdown
                              components={{
                                strong: ({node, ...props}) => <strong className="font-bold text-[#34c759]" {...props} />,
                                p: ({node, ...props}) => <p className="mb-3 text-[#dcdcdc]" {...props} />,
                                ul: ({node, ...props}) => <ul className="list-disc ml-6 mb-3 space-y-1" {...props} />,
                                li: ({node, ...props}) => <li className="text-[#dcdcdc]" {...props} />,
                                h2: ({node, ...props}) => <h2 className="text-lg font-semibold mt-4 mb-2 text-[#dcdcdc]" {...props} />,
                                h3: ({node, ...props}) => <h3 className="text-base font-semibold mt-3 mb-2 text-[#dcdcdc]" {...props} />,
                              }}
                            >
                              {expandedResponses[modelId] || response.content.length <= MAX_PREVIEW_LENGTH
                                ? response.content
                                : `${response.content.slice(0, MAX_PREVIEW_LENGTH)}...`}
                            </ReactMarkdown>
                          </div>
                          {response.content.length > MAX_PREVIEW_LENGTH && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleExpand(modelId)}
                              className="mt-2 text-[#34c759] hover:text-[#34c759] hover:bg-[#1a2e1a]/30"
                            >
                              {expandedResponses[modelId] ? "Show Less" : "Show More"}
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
          </div>
          {showSuggestions && (
            <div className="px-4 pb-2 border-t border-[#2d3237] bg-gradient-to-b from-[#141820] to-[#1a1e23]">
              <div className="w-full flex items-center py-2">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-1.5 rounded-full bg-[#34c759] animate-pulse"></div>
                  <p className="text-xs font-bold text-[#34c759] uppercase tracking-widest">
                    Try These Prompts
                  </p>
                </div>
              </div>
              
              <div className="pb-3 space-y-3">
                  {/* Market & Analysis (combined stock prices and analysis) */}
                  <div className="space-y-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedCategory(expandedCategory === "market" ? null : "market");
                      }}
                      className="flex items-center justify-between w-full text-left px-2 py-1.5 rounded-md hover:bg-[#23272c] transition-colors cursor-pointer"
                    >
                      <p className="text-xs font-semibold text-[#9ca3af] uppercase tracking-wide">Market & Analysis</p>
                      {expandedCategory === "market" ? (
                        <ChevronUp className="h-3 w-3 text-[#9ca3af]" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-[#9ca3af]" />
                      )}
                    </button>
                    {expandedCategory === "market" && (
                      <div className="flex flex-wrap gap-1.5">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "market").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-2.5 py-1.5 text-xs rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                          >
                            {suggestion.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Setup & Education */}
                  <div className="space-y-1.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setExpandedCategory(expandedCategory === "setup" ? null : "setup");
                      }}
                      className="flex items-center justify-between w-full text-left px-2 py-1.5 rounded-md hover:bg-[#23272c] transition-colors cursor-pointer"
                    >
                      <p className="text-xs font-semibold text-[#9ca3af] uppercase tracking-wide">Setup & Education</p>
                      {expandedCategory === "setup" ? (
                        <ChevronUp className="h-3 w-3 text-[#9ca3af]" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-[#9ca3af]" />
                      )}
                    </button>
                    {expandedCategory === "setup" && (
                      <div className="flex flex-wrap gap-1.5">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "setup").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-2.5 py-1.5 text-xs rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                          >
                            {suggestion.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
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
              disabled={isLoading || selectedModelIds.length === 0}
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

