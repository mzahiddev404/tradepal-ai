"use client";

/**
 * Model Selector Component
 * 
 * Allows users to select individual models from any provider to compare.
 */

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { X } from "lucide-react";
import { getAllAvailableModels, type ModelInfo } from "@/lib/llm-providers";

interface ModelSelectorProps {
  selectedModelIds: string[]; // Array of "provider:model" IDs
  onModelsChange: (modelIds: string[]) => void;
}

export function ModelSelector({
  selectedModelIds,
  onModelsChange,
}: ModelSelectorProps) {
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    getAllAvailableModels().then(setAvailableModels);
  }, []);

  const handleAddModel = (modelId: string) => {
    if (!selectedModelIds.includes(modelId)) {
      onModelsChange([...selectedModelIds, modelId]);
    }
  };

  const handleRemoveModel = (modelId: string) => {
    onModelsChange(selectedModelIds.filter((id) => id !== modelId));
  };

  const getAvailableOptions = () => {
    return availableModels.filter((model) => !selectedModelIds.includes(model.id));
  };

  if (availableModels.length === 0) {
    return (
      <Card className="trading-panel border-[#2d3237]">
        <CardHeader className="trading-panel-header">
          <CardTitle className="text-[#dcdcdc] text-sm font-mono uppercase tracking-wide">Configuration Required</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <p className="text-[#9ca3af] text-sm mb-4 font-mono">
            [SYSTEM WARNING] No API keys detected. Comparison module offline.
          </p>
          <Button
            variant="outline"
            onClick={() => (window.location.href = "/settings")}
            className="border-[#34c759] text-[#34c759] hover:bg-[#1a2e1a] font-mono text-xs h-8"
          >
            CONFIGURE_KEYS
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="trading-panel border-[#2d3237]">
      <CardHeader className="trading-panel-header flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-[#dcdcdc] text-sm font-mono uppercase tracking-wide">
          Comparison Matrix
        </CardTitle>
        <div className="flex gap-1">
          <div className="h-1.5 w-1.5 rounded-full bg-[#34c759] animate-pulse"></div>
          <div className="h-1.5 w-1.5 rounded-full bg-[#007aff] animate-pulse delay-75"></div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-4">
        {/* Selected Models */}
        {selectedModelIds.length > 0 && (
          <div className="space-y-2">
            <Label className="text-[10px] text-[#9ca3af] uppercase tracking-widest font-bold">Active Engines</Label>
            <div className="space-y-2">
              {selectedModelIds.map((modelId) => {
                const modelInfo = availableModels.find((m) => m.id === modelId);
                if (!modelInfo) return null;
                return (
                  <div
                    key={modelId}
                    className="flex items-center justify-between rounded border border-[#34c759]/30 bg-[#34c759]/5 p-2 pl-3 transition-all hover:bg-[#34c759]/10"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 font-mono text-xs">
                        <span className="text-[#34c759] font-bold">
                          {modelInfo.providerName.toUpperCase()}
                        </span>
                        <span className="text-[#9ca3af]">::</span>
                        <span className="text-[#dcdcdc]">{modelInfo.model}</span>
                        <span className="text-[#9ca3af]">::</span>
                        <span className="text-[#9ca3af]">{modelInfo.cost}</span>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveModel(modelId)}
                      className="h-6 w-6 p-0 text-[#9ca3af] hover:text-[#ff3b30] hover:bg-transparent"
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Add Model Dropdown */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label className="text-[10px] text-[#9ca3af] uppercase tracking-widest font-bold">
              {selectedModelIds.length === 0 ? "Select Engine" : "Add Engine"}
            </Label>
            <span className="text-[10px] text-[#9ca3af] font-mono">
              COST_INDEX: $ - $$$$
            </span>
          </div>
          <Select
            value=""
            onValueChange={handleAddModel}
            disabled={getAvailableOptions().length === 0}
          >
            <SelectTrigger className="border-[#2d3237] bg-[#141820] text-[#dcdcdc] hover:border-[#34c759] h-9 font-mono text-xs">
              <SelectValue placeholder="INITIALIZE_NEW_MODEL..." className="text-[#dcdcdc]" />
            </SelectTrigger>
            <SelectContent className="border-[#2d3237] bg-[#1a1e23] text-[#dcdcdc]">
              {getAvailableOptions().map((model) => {
                const getCostColor = (cost: string) => {
                  if (cost === "$") return "text-[#34c759]";
                  if (cost === "$$") return "text-[#ff9500]";
                  if (cost === "$$$") return "text-[#ff3b30]";
                  if (cost === "$$$$") return "text-[#af52de]";
                  return "text-[#9ca3af]";
                };

                const costColor = getCostColor(model.cost);
                
                return (
                  <SelectItem
                    key={model.id}
                    value={model.id}
                    className="text-[#dcdcdc] focus:bg-[#23272c] focus:text-[#34c759] hover:bg-[#23272c] hover:text-[#34c759] cursor-pointer font-mono text-xs"
                  >
                    <div className="flex items-center justify-between w-full min-w-[200px]">
                      <div className="flex items-center gap-2">
                        <span className="text-[#9ca3af]">{model.providerName.toUpperCase()}</span>
                        <span className="text-[#9ca3af]">/</span>
                        <span>{model.model}</span>
                      </div>
                      <span className={`ml-4 ${costColor} font-bold`}>{model.cost}</span>
                    </div>
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>

        {selectedModelIds.length === 0 && (
          <p className="text-xs text-[#9ca3af] text-center py-4 font-mono animate-pulse">
            _WAITING_FOR_SELECTION
          </p>
        )}
      </CardContent>
    </Card>
  );
}
