"use client";

/**
 * Model Selector Component
 * 
 * Allows users to select which LLM providers and models to compare.
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
import { Check, X } from "lucide-react";
import { PROVIDER_CONFIGS, getAvailableProviders, getModelCost, type ProviderType } from "@/lib/llm-providers";
import { cn } from "@/lib/utils";

interface ModelSelectorProps {
  selectedProviders: ProviderType[];
  selectedModels: Record<ProviderType, string>;
  onProvidersChange: (providers: ProviderType[]) => void;
  onModelsChange: (models: Record<ProviderType, string>) => void;
}

export function ModelSelector({
  selectedProviders,
  selectedModels,
  onProvidersChange,
  onModelsChange,
}: ModelSelectorProps) {
  const [availableProviders, setAvailableProviders] = useState<ProviderType[]>([]);

  useEffect(() => {
    getAvailableProviders().then(setAvailableProviders);
  }, []);

  const toggleProvider = (provider: ProviderType) => {
    if (selectedProviders.includes(provider)) {
      onProvidersChange(selectedProviders.filter((p) => p !== provider));
    } else {
      onProvidersChange([...selectedProviders, provider]);
      // Set default model for newly selected provider
      const config = PROVIDER_CONFIGS[provider];
      onModelsChange({
        ...selectedModels,
        [provider]: config.defaultModel,
      });
    }
  };

  const handleModelChange = (provider: ProviderType, model: string) => {
    onModelsChange({
      ...selectedModels,
      [provider]: model,
    });
  };

  if (availableProviders.length === 0) {
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
        {availableProviders.map((provider) => {
          const config = PROVIDER_CONFIGS[provider];
          const isSelected = selectedProviders.includes(provider);
          const currentModel = selectedModels[provider] || config.defaultModel;

          return (
            <div
              key={provider}
              className={cn(
                "rounded-lg border p-4 transition-colors",
                isSelected
                  ? "border-[#34c759] bg-[#1a2e1a]/30"
                  : "border-[#2d3237] bg-[#141820]"
              )}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => toggleProvider(provider)}
                    className={cn(
                      "flex h-5 w-5 items-center justify-center rounded border transition-colors",
                      isSelected
                        ? "border-[#34c759] bg-[#34c759]"
                        : "border-[#6b7280] bg-transparent"
                    )}
                  >
                    {isSelected && <Check className="h-3 w-3 text-white" />}
                  </button>
                  <div>
                    <Label className="text-[#dcdcdc] font-medium">{config.name}</Label>
                    <p className="text-xs text-[#9ca3af]">{config.description}</p>
                  </div>
                </div>
              </div>
              {isSelected && (
                <div className="mt-3">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-sm text-[#9ca3af]">Model</Label>
                    <span className="text-xs text-[#9ca3af]">
                      $ = Low • $$ = Medium • $$$ = High • $$$$ = Premium
                    </span>
                  </div>
                  <Select
                    value={currentModel}
                    onValueChange={(value) => handleModelChange(provider, value)}
                  >
                    <SelectTrigger className="border-[#2d3237] bg-[#141820] text-[#dcdcdc] hover:border-[#34c759]">
                      <div className="flex items-center justify-between w-full">
                        <SelectValue className="text-[#dcdcdc]" />
                        <span className="text-xs text-[#9ca3af] ml-2">{getModelCost(currentModel)}</span>
                      </div>
                    </SelectTrigger>
                    <SelectContent className="border-[#2d3237] bg-[#1a1e23] text-[#dcdcdc]">
                      {config.models.map((model) => {
                        const cost = getModelCost(model);
                        return (
                          <SelectItem 
                            key={model} 
                            value={model}
                            className="text-[#dcdcdc] focus:bg-[#23272c] focus:text-[#34c759] hover:bg-[#23272c] hover:text-[#34c759] cursor-pointer"
                          >
                            <div className="flex items-center justify-between w-full">
                              <span>{model}</span>
                              <span className="ml-2 text-[#9ca3af] text-xs">{cost}</span>
                            </div>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          );
        })}
        {selectedProviders.length === 0 && (
          <p className="text-sm text-[#9ca3af] text-center py-4">
            Select at least one provider to compare
          </p>
        )}
      </CardContent>
    </Card>
  );
}

