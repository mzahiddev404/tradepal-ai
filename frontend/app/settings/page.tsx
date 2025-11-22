"use client";

/**
 * Settings Page
 * 
 * API key management interface for multi-LLM comparison feature.
 * Allows users to securely store API keys for different LLM providers.
 */

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  storeApiKey,
  getApiKeyMetadata,
  removeApiKey,
  clearAllApiKeys,
  validateApiKeyFormat,
  listStoredProviders,
  type ProviderType,
} from "@/lib/api-keys";
import { PROVIDER_CONFIGS } from "@/lib/llm-providers";
import { Check, X, Trash2, AlertCircle } from "lucide-react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { MarketTime } from "@/components/chat/market-time";
import { useRouter } from "next/navigation";

export default function SettingsPage() {
  const router = useRouter();
  const [apiKeys, setApiKeys] = useState<Record<ProviderType, string>>({
    openai: "",
    anthropic: "",
    google: "",
    openrouter: "",
  } as Record<ProviderType, string>);
  const [savedStatus, setSavedStatus] = useState<Record<ProviderType, boolean>>({
    openai: false,
    anthropic: false,
    google: false,
    openrouter: false,
  } as Record<ProviderType, boolean>);
  const [errors, setErrors] = useState<Record<ProviderType, string>>({} as Record<ProviderType, string>);
  const [isSaving, setIsSaving] = useState<Record<ProviderType, boolean>>({
    openai: false,
    anthropic: false,
    google: false,
    openrouter: false,
  } as Record<ProviderType, boolean>);

  useEffect(() => {
    // Check which providers have stored keys
    const stored = listStoredProviders();
    const status: Record<ProviderType, boolean> = {
      openai: false,
      anthropic: false,
      google: false,
      openrouter: false,
    };
    stored.forEach((provider) => {
      status[provider] = true;
    });
    setSavedStatus(status);
  }, []);

  const handleSave = async (provider: ProviderType) => {
    const key = apiKeys[provider].trim();
    
    if (!key) {
      setErrors((prev) => ({ ...prev, [provider]: "API key cannot be empty" }));
      return;
    }

    if (!validateApiKeyFormat(provider, key)) {
      setErrors((prev) => ({
        ...prev,
        [provider]: `Invalid API key format for ${PROVIDER_CONFIGS[provider].name}`,
      }));
      return;
    }

    setIsSaving((prev) => ({ ...prev, [provider]: true }));
    setErrors((prev => ({ ...prev, [provider]: "" })));

    try {
      await storeApiKey(provider, key);
      setSavedStatus((prev) => ({ ...prev, [provider]: true }));
      setApiKeys((prev) => ({ ...prev, [provider]: "" }));
    } catch (error) {
      setErrors((prev) => ({
        ...prev,
        [provider]: error instanceof Error ? error.message : "Failed to save API key",
      }));
    } finally {
      setIsSaving((prev) => ({ ...prev, [provider]: false }));
    }
  };

  const handleRemove = (provider: ProviderType) => {
    removeApiKey(provider);
    setSavedStatus((prev) => ({ ...prev, [provider]: false }));
    setApiKeys((prev) => ({ ...prev, [provider]: "" }));
    setErrors((prev => ({ ...prev, [provider]: "" })));
  };

  const handleClearAll = () => {
    if (confirm("Are you sure you want to remove all API keys? This action cannot be undone.")) {
      clearAllApiKeys();
      setSavedStatus({
        openai: false,
        anthropic: false,
        google: false,
        openrouter: false,
      });
      setApiKeys({
        openai: "",
        anthropic: "",
        google: "",
        openrouter: "",
      });
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#0F1115] bg-grid-subtle text-[#dcdcdc] overflow-hidden">
      <AppSidebar 
        chatMode="standard"
        onModeChange={() => router.push("/")}
        showDocuments={false}
        onToggleDocuments={() => router.push("/")}
      />
      
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-14 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 bg-[#131619]/50 backdrop-blur-sm shrink-0 z-10">
           <div className="flex items-center gap-3 md:hidden">
             <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-[#34c759] to-[#28a745]">
               <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
               </svg>
             </div>
             <span className="font-bold text-white tracking-tight">TRADEPAL</span>
          </div>

          <div className="hidden md:flex items-center text-sm font-medium text-gray-400">
             <span className="text-gray-500">System</span>
             <span className="mx-2">/</span>
             <span className="text-white">Settings</span>
          </div>

          <div className="flex items-center gap-4">
            <MarketTime />
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 md:p-8 custom-scrollbar">
          <div className="max-w-4xl mx-auto">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-[#dcdcdc] mb-2">API Key Settings</h1>
              <p className="text-[#9ca3af]">
                Manage API keys for multi-LLM comparison. Keys are encrypted and stored locally in your browser.
              </p>
            </div>

            <div className="mb-6 rounded-lg border border-[#ff9500]/30 bg-[#2d1f1f] p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-[#ff9500] mt-0.5 flex-shrink-0" />
                <div className="text-sm text-[#ff9500]">
                  <p className="font-semibold mb-1">Security Notice</p>
                  <p className="text-[#ffcc80]">
                    API keys are encrypted and stored locally in your browser. They are never sent to our servers.
                    Make sure to keep your keys secure and never share them publicly.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {(Object.keys(PROVIDER_CONFIGS) as ProviderType[]).map((provider) => {
                const config = PROVIDER_CONFIGS[provider];
                const hasKey = savedStatus[provider];
                const error = errors[provider];
                const saving = isSaving[provider];

                return (
                  <Card
                    key={provider}
                    className="trading-panel border-[#2d3237]"
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="text-[#dcdcdc]">{config.name}</CardTitle>
                          <CardDescription className="text-[#9ca3af]">
                            {config.description}
                          </CardDescription>
                        </div>
                        {hasKey && (
                          <div className="flex items-center gap-2 text-[#34c759]">
                            <Check className="h-4 w-4" />
                            <span className="text-sm font-medium">Configured</span>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor={provider} className="text-[#dcdcdc] mb-2 block">
                            API Key
                          </Label>
                          <div className="flex gap-2">
                            <Input
                              id={provider}
                              type="password"
                              placeholder={`Enter your ${config.name} API key`}
                              value={apiKeys[provider]}
                              onChange={(e) =>
                                setApiKeys((prev) => ({ ...prev, [provider]: e.target.value }))
                              }
                              className="flex-1 border-[#2d3237] bg-[#141820] text-[#dcdcdc] placeholder:text-[#6b7280] focus:border-[#34c759] focus:ring-[#34c759]/20"
                              disabled={saving}
                            />
                            {hasKey ? (
                              <Button
                                variant="outline"
                                onClick={() => handleRemove(provider)}
                                className="border-[#ff3b30] text-[#ff3b30] hover:bg-[#2d1f1f]"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            ) : (
                              <Button
                                onClick={() => handleSave(provider)}
                                disabled={saving || !apiKeys[provider].trim()}
                                className="bg-[#34c759] hover:bg-[#28a745] text-white"
                              >
                                {saving ? "Saving..." : "Save"}
                              </Button>
                            )}
                          </div>
                          {error && (
                            <p className="mt-2 text-sm text-[#ff3b30]">{error}</p>
                          )}
                        </div>
                        {hasKey && (
                          <div className="text-xs text-[#9ca3af]">
                            API key is stored and encrypted. You can remove it using the trash icon above.
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div className="mt-6 flex justify-end">
              <Button
                variant="outline"
                onClick={handleClearAll}
                className="border-[#ff3b30] text-[#ff3b30] hover:bg-[#2d1f1f]"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Clear All Keys
              </Button>
            </div>

            <div className="mt-8 rounded-lg border border-[#2d3237] bg-[#1a1e23]/50 p-6 glass-panel">
              <h3 className="text-lg font-semibold text-[#dcdcdc] mb-3">Getting API Keys</h3>
              <div className="space-y-2 text-sm text-[#9ca3af]">
                <p>
                  <strong className="text-[#dcdcdc]">OpenAI:</strong>{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#34c759] hover:underline"
                  >
                    platform.openai.com/api-keys
                  </a>
                </p>
                <p>
                  <strong className="text-[#dcdcdc]">Anthropic:</strong>{" "}
                  <a
                    href="https://console.anthropic.com/settings/keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#34c759] hover:underline"
                  >
                    console.anthropic.com/settings/keys
                  </a>
                </p>
                <p>
                  <strong className="text-[#dcdcdc]">Google Gemini:</strong>{" "}
                  <a
                    href="https://makersuite.google.com/app/apikey"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#34c759] hover:underline"
                  >
                    makersuite.google.com/app/apikey
                  </a>
                </p>
                <p>
                  <strong className="text-[#dcdcdc]">OpenRouter:</strong>{" "}
                  <a
                    href="https://openrouter.ai/keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[#34c759] hover:underline"
                  >
                    openrouter.ai/keys
                  </a>{" "}
                  (Single key for multiple models)
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
