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
import { getAllAvailableModels, type ModelInfo, parseModelId } from "@/lib/llm-providers";
import { cn } from "@/lib/utils";

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
      <Card className="border-[#2d3237] bg-[#1a1e23]/95">
        <CardHeader>
          <CardTitle className="text-[#dcdcdc]">No Providers Configured</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-[#9ca3af] text-sm mb-4">
            Please configure at least one API key in Settings to use multi-LLM comparison.
          </p>
          <Button
            variant="outline"
            onClick={() => (window.location.href = "/settings")}
            className="border-[#34c759] text-[#34c759] hover:bg-[#1a2e1a]"
          >
            Go to Settings
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-[#2d3237] bg-[#1a1e23]/95">
      <CardHeader>
        <CardTitle className="text-[#dcdcdc]">Select Models to Compare</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Selected Models */}
        {selectedModelIds.length > 0 && (
          <div className="space-y-2">
            <Label className="text-sm text-[#9ca3af]">Selected Models</Label>
            <div className="space-y-2">
              {selectedModelIds.map((modelId) => {
                const modelInfo = availableModels.find((m) => m.id === modelId);
                if (!modelInfo) return null;
                return (
                  <div
                    key={modelId}
                    className="flex items-center justify-between rounded-lg border border-[#34c759] bg-[#1a2e1a]/30 p-3"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-[#dcdcdc]">
                          {modelInfo.providerName}
                        </span>
                        <span className="text-xs text-[#9ca3af]">•</span>
                        <span className="text-sm text-[#dcdcdc]">{modelInfo.model}</span>
                        <span className="text-xs text-[#9ca3af]">•</span>
                        <span className="text-xs text-[#9ca3af]">{modelInfo.cost}</span>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveModel(modelId)}
                      className="h-6 w-6 p-0 text-[#9ca3af] hover:text-[#ff3b30]"
                    >
                      <X className="h-4 w-4" />
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
            <Label className="text-sm text-[#9ca3af]">
              {selectedModelIds.length === 0 ? "Add Models" : "Add Another Model"}
            </Label>
            <span className="text-xs text-[#9ca3af]">
              $ = Low • $$ = Medium • $$$ = High • $$$$ = Premium
            </span>
          </div>
          <Select
            value=""
            onValueChange={handleAddModel}
            disabled={getAvailableOptions().length === 0}
          >
            <SelectTrigger className="border-[#2d3237] bg-[#141820] text-[#dcdcdc] hover:border-[#34c759]">
              <SelectValue placeholder="Select a model to add..." className="text-[#dcdcdc]" />
            </SelectTrigger>
            <SelectContent className="border-[#2d3237] bg-[#1a1e23] text-[#dcdcdc]">
              {getAvailableOptions().map((model) => (
                <SelectItem
                  key={model.id}
                  value={model.id}
                  className="text-[#dcdcdc] focus:bg-[#23272c] focus:text-[#34c759] hover:bg-[#23272c] hover:text-[#34c759] cursor-pointer"
                >
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-[#9ca3af]">{model.providerName}</span>
                      <span className="text-xs text-[#9ca3af]">•</span>
                      <span>{model.model}</span>
                    </div>
                    <span className="ml-2 text-[#9ca3af] text-xs">{model.cost}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedModelIds.length === 0 && (
          <p className="text-sm text-[#9ca3af] text-center py-4">
            Select at least one model to compare
          </p>
        )}
      </CardContent>
    </Card>
  );
}
