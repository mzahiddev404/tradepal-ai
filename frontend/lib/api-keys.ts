/**
 * API Key Management Utilities
 * 
 * Secure storage and retrieval of API keys using Web Crypto API encryption.
 * Keys are stored in localStorage with encryption to prevent plaintext exposure.
 */

const STORAGE_PREFIX = "tradepal_api_keys_";
const ENCRYPTION_KEY_NAME = "tradepal_encryption_key";

/**
 * Generate or retrieve encryption key for API keys
 */
async function getEncryptionKey(): Promise<CryptoKey> {
  // Check if key exists in sessionStorage (temporary, cleared on close)
  const keyData = sessionStorage.getItem(ENCRYPTION_KEY_NAME);
  
  if (keyData) {
    const keyBuffer = Uint8Array.from(JSON.parse(keyData));
    return await crypto.subtle.importKey(
      "raw",
      keyBuffer,
      { name: "AES-GCM" },
      false,
      ["encrypt", "decrypt"]
    );
  }

  // Generate new key
  const key = await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );

  const exported = await crypto.subtle.exportKey("raw", key);
  sessionStorage.setItem(ENCRYPTION_KEY_NAME, JSON.stringify(Array.from(new Uint8Array(exported))));

  return key;
}

/**
 * Encrypt API key before storage
 */
async function encryptKey(plaintext: string): Promise<string> {
  const key = await getEncryptionKey();
  const encoder = new TextEncoder();
  const data = encoder.encode(plaintext);
  
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    data
  );

  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(encrypted), iv.length);

  return btoa(String.fromCharCode(...combined));
}

/**
 * Decrypt API key from storage
 */
async function decryptKey(ciphertext: string): Promise<string> {
  try {
    const key = await getEncryptionKey();
    const combined = Uint8Array.from(atob(ciphertext), c => c.charCodeAt(0));
    
    const iv = combined.slice(0, 12);
    const data = combined.slice(12);

    const decrypted = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv },
      key,
      data
    );

    const decoder = new TextDecoder();
    return decoder.decode(decrypted);
  } catch (error) {
    throw new Error("Failed to decrypt API key. It may be corrupted.");
  }
}

export type ProviderType = "openai" | "anthropic" | "google" | "openrouter";

export interface StoredApiKey {
  provider: ProviderType;
  key: string;
  label?: string;
  createdAt: string;
}

/**
 * Store an API key securely
 */
export async function storeApiKey(
  provider: ProviderType,
  apiKey: string,
  label?: string
): Promise<void> {
  if (!apiKey.trim()) {
    throw new Error("API key cannot be empty");
  }

  const encrypted = await encryptKey(apiKey);
  const stored: StoredApiKey = {
    provider,
    key: encrypted,
    label,
    createdAt: new Date().toISOString(),
  };

  localStorage.setItem(`${STORAGE_PREFIX}${provider}`, JSON.stringify(stored));
}

/**
 * Retrieve and decrypt an API key
 */
export async function getApiKey(provider: ProviderType): Promise<string | null> {
  const stored = localStorage.getItem(`${STORAGE_PREFIX}${provider}`);
  if (!stored) {
    return null;
  }

  try {
    const data: StoredApiKey = JSON.parse(stored);
    return await decryptKey(data.key);
  } catch (error) {
    console.error(`Failed to retrieve API key for ${provider}:`, error);
    return null;
  }
}

/**
 * Get stored API key metadata (without decryption)
 */
export function getApiKeyMetadata(provider: ProviderType): Omit<StoredApiKey, "key"> | null {
  const stored = localStorage.getItem(`${STORAGE_PREFIX}${provider}`);
  if (!stored) {
    return null;
  }

  try {
    const data: StoredApiKey = JSON.parse(stored);
    return {
      provider: data.provider,
      label: data.label,
      createdAt: data.createdAt,
    };
  } catch {
    return null;
  }
}

/**
 * Check if an API key exists for a provider
 */
export function hasApiKey(provider: ProviderType): boolean {
  return localStorage.getItem(`${STORAGE_PREFIX}${provider}`) !== null;
}

/**
 * Remove an API key
 */
export function removeApiKey(provider: ProviderType): void {
  localStorage.removeItem(`${STORAGE_PREFIX}${provider}`);
}

/**
 * Remove all API keys
 */
export function clearAllApiKeys(): void {
  Object.values(["openai", "anthropic", "google", "openrouter"] as ProviderType[]).forEach(
    (provider) => {
      removeApiKey(provider);
    }
  );
}

/**
 * List all providers with stored keys
 */
export function listStoredProviders(): ProviderType[] {
  const providers: ProviderType[] = [];
  const allProviders: ProviderType[] = ["openai", "anthropic", "google", "openrouter"];

  allProviders.forEach((provider) => {
    if (hasApiKey(provider)) {
      providers.push(provider);
    }
  });

  return providers;
}

/**
 * Validate API key format (basic validation)
 */
export function validateApiKeyFormat(provider: ProviderType, key: string): boolean {
  if (!key.trim()) {
    return false;
  }

  switch (provider) {
    case "openai":
      return key.startsWith("sk-") && key.length > 20;
    case "anthropic":
      return key.startsWith("sk-ant-") && key.length > 20;
    case "google":
      return key.length > 20; // Google API keys vary in format
    case "openrouter":
      return key.startsWith("sk-or-") && key.length > 20;
    default:
      return key.length > 10;
  }
}

