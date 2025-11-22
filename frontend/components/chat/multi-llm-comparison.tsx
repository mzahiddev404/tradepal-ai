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
import { AlertCircle, CheckCircle, XCircle, ChevronDown, ChevronUp, Terminal } from "lucide-react";
import { cn } from "@/lib/utils";
import { CHAT_SUGGESTIONS } from "@/constants/chat";
import ReactMarkdown from "react-markdown";

export function MultiLLMComparison() {
  const [selectedModelIds, setSelectedModelIds] = useState<string[]>([]);
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [showSelector, setShowSelector] = useState(true);
  const [expandedResponses, setExpandedResponses] = useState<Record<string, boolean>>({});
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
  
  const showSuggestions = selectedModelIds.length > 0 && (!showSelector || allResponsesCompleted);

  const toggleExpand = (modelId: string) => {
    setExpandedResponses((prev) => ({
      ...prev,
      [modelId]: !prev[modelId],
    }));
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
    setExpandedCategory(null);
  };

  const MAX_PREVIEW_LENGTH = 500;

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#0F1115] relative">
      {/* Grid Background */}
      <div className="absolute inset-0 bg-grid-subtle opacity-50 pointer-events-none"></div>

      {showSelector && (
        <>
          <div className="p-4 sm:p-6 border-b border-white/5 bg-[#131619]/50 backdrop-blur-sm z-10">
            <ModelSelector
              selectedModelIds={selectedModelIds}
              onModelsChange={setSelectedModelIds}
            />
          </div>
          
          {selectedModelIds.length > 0 && (
            <div className="px-4 sm:px-6 py-3 border-b border-white/5 bg-[#131619]/30 z-10">
              <div className="flex items-center gap-2 mb-3">
                <Terminal className="h-3 w-3 text-[#34c759]" />
                <p className="text-[10px] font-bold text-[#34c759] uppercase tracking-widest">
                  Quick Execute
                </p>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {/* Market & Analysis */}
                  <div className="space-y-1">
                    <button
                      onClick={() => setExpandedCategory(expandedCategory === "market" ? null : "market")}
                      className="flex items-center justify-between w-full px-3 py-2 rounded border border-white/5 bg-white/5 hover:bg-white/10 transition-all text-left group"
                    >
                      <span className="text-xs font-mono text-gray-400 group-hover:text-white transition-colors uppercase tracking-wide">Market_Analysis</span>
                      {expandedCategory === "market" ? (
                        <ChevronUp className="h-3 w-3 text-gray-500" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-gray-500" />
                      )}
                    </button>
                    {expandedCategory === "market" && (
                      <div className="grid grid-cols-1 gap-1 pl-2 border-l border-white/10 animate-in fade-in slide-in-from-top-1">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "market").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-3 py-1.5 text-xs text-left text-gray-400 hover:text-[#34c759] hover:bg-white/5 rounded-sm transition-all font-mono truncate"
                          >
                            {">"} {suggestion.text}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Setup & Education */}
                  <div className="space-y-1">
                    <button
                      onClick={() => setExpandedCategory(expandedCategory === "setup" ? null : "setup")}
                      className="flex items-center justify-between w-full px-3 py-2 rounded border border-white/5 bg-white/5 hover:bg-white/10 transition-all text-left group"
                    >
                      <span className="text-xs font-mono text-gray-400 group-hover:text-white transition-colors uppercase tracking-wide">Setup_Education</span>
                      {expandedCategory === "setup" ? (
                        <ChevronUp className="h-3 w-3 text-gray-500" />
                      ) : (
                        <ChevronDown className="h-3 w-3 text-gray-500" />
                      )}
                    </button>
                    {expandedCategory === "setup" && (
                      <div className="grid grid-cols-1 gap-1 pl-2 border-l border-white/10 animate-in fade-in slide-in-from-top-1">
                        {CHAT_SUGGESTIONS.filter(s => s.category === "setup").map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSuggestionClick(suggestion.text)}
                            disabled={isLoading}
                            className="px-3 py-1.5 text-xs text-left text-gray-400 hover:text-[#34c759] hover:bg-white/5 rounded-sm transition-all font-mono truncate"
                          >
                            {">"} {suggestion.text}
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
        <div className="flex-1 overflow-hidden flex flex-col min-h-0 z-10">
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 auto-rows-min">
              {selectedModelIds.map((modelId) => {
                const modelInfo = availableModels.find((m) => m.id === modelId);
                if (!modelInfo) return null;
                
                const response = responses[modelId];

                return (
                  <Card
                    key={modelId}
                    className={cn(
                      "trading-panel border-[#2d3237] flex flex-col transition-all duration-300 hover:border-[#34c759]/30 hover:shadow-[0_0_20px_rgba(52,199,89,0.05)]",
                      response?.error && "border-[#ff3b30]/50 shadow-[0_0_20px_rgba(255,59,48,0.05)]",
                      response?.completed && !response.error && "border-[#34c759]/50"
                    )}
                  >
                    <CardHeader className="trading-panel-header py-3">
                      <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                          <div className="flex items-center gap-2">
                            <div className={cn("w-1.5 h-1.5 rounded-full", response?.completed ? "bg-[#34c759]" : response?.error ? "bg-[#ff3b30]" : "bg-[#007aff] animate-pulse")}></div>
                            <CardTitle className="text-[#dcdcdc] text-sm font-mono uppercase tracking-wide">
                              {modelInfo.providerName}
                            </CardTitle>
                          </div>
                          <div className="flex items-center gap-2 mt-1 ml-3.5">
                            <span className="text-[10px] text-[#9ca3af] font-mono">{modelInfo.model}</span>
                            <span className="text-[10px] text-[#9ca3af]">•</span>
                            <span className="text-[10px] text-[#34c759] font-bold">{modelInfo.cost}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {response?.isLoading && (
                            <Spinner className="h-3 w-3 text-[#007aff]" />
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
                    <CardContent className="p-4 flex-1">
                      {response?.isLoading && !response.content && (
                        <div className="flex items-center gap-2 text-[#9ca3af] h-20 justify-center">
                          <span className="h-1 w-1 bg-[#007aff] rounded-full animate-bounce"></span>
                          <span className="h-1 w-1 bg-[#007aff] rounded-full animate-bounce delay-75"></span>
                          <span className="h-1 w-1 bg-[#007aff] rounded-full animate-bounce delay-150"></span>
                          <span className="text-xs font-mono ml-2 animate-pulse">AWAITING_STREAM...</span>
                        </div>
                      )}
                      {response?.error && (
                        <div className="rounded border border-[#ff3b30]/30 bg-[#ff3b30]/5 p-3">
                          <div className="flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-[#ff3b30] mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <p className="text-xs text-[#ff6b6b] font-mono">{response.error}</p>
                            </div>
                          </div>
                        </div>
                      )}
                      {response?.content && (
                        <div className="prose prose-invert max-w-none">
                          <div className="text-gray-300 text-sm leading-relaxed font-sans">
                            <ReactMarkdown
                              components={{
                                strong: ({node, ...props}) => <strong className="font-bold text-[#34c759]" {...props} />,
                                p: ({node, ...props}) => <p className="mb-3 text-gray-300 last:mb-0" {...props} />,
                                ul: ({node, ...props}) => <ul className="list-disc ml-4 mb-3 space-y-1 marker:text-[#34c759]" {...props} />,
                                li: ({node, ...props}) => <li className="text-gray-300 pl-1" {...props} />,
                                code: ({node, ...props}) => <code className="bg-black/30 px-1 py-0.5 rounded text-[#34c759] font-mono text-xs border border-white/5" {...props} />,
                                pre: ({node, ...props}) => <pre className="bg-black/30 p-3 rounded-lg border border-white/5 overflow-x-auto mb-3" {...props} />,
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
                              className="mt-3 w-full h-8 text-[#34c759] hover:text-[#34c759] hover:bg-[#34c759]/10 font-mono text-xs border border-[#34c759]/20"
                            >
                              {expandedResponses[modelId] ? "COLLAPSE_VIEW" : "EXPAND_VIEW"}
                            </Button>
                          )}
                        </div>
                      )}
                      {!response && !isLoading && (
                        <div className="h-32 flex items-center justify-center border border-dashed border-white/10 rounded">
                          <p className="text-xs text-[#9ca3af] font-mono">IDLE_STATE</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
            {!hasResponses && !isLoading && (
              <div className="flex items-center justify-center h-full min-h-[200px] opacity-50">
                <div className="text-center space-y-2">
                  <Terminal className="h-8 w-8 text-[#9ca3af] mx-auto mb-2" />
                  <p className="text-[#9ca3af] text-xs font-mono">
                    SYSTEM_READY // AWAITING_INPUT
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {error && (
        <div className="mx-4 sm:mx-6 mb-4 rounded border border-[#ff3b30]/30 bg-[#ff3b30]/10 p-3 backdrop-blur-md z-10 animate-in fade-in slide-in-from-bottom-2">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-[#ff3b30] flex-shrink-0" />
            <p className="text-xs text-[#ff6b6b] font-mono">ERROR: {error}</p>
          </div>
        </div>
      )}

      <div className="border-t border-white/5 bg-[#131619]/80 p-4 sm:p-6 backdrop-blur-md z-20">
        <div className="flex gap-3">
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
              className="border-[#ff3b30]/30 text-[#ff3b30] hover:bg-[#ff3b30]/10 h-12 w-12 p-0 shrink-0"
            >
              <XCircle className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
