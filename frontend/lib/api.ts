/**
 * API client for backend communication
 * Refactored with better error handling and separation of concerns
 */

import { apiRequest } from "./api-client";
import { API_URL } from "./constants";

export interface ChatMessage {
  role: string;
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  status: string;
  agent_name?: string;
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  history: ChatMessage[] = []
): Promise<string> {
  const data = await apiRequest<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      message,
      history,
    } as ChatRequest),
  });

  return data.message;
}

/**
 * Check backend health
 */
export async function checkHealth(): Promise<boolean> {
  try {
    await apiRequest("/api/health");
    return true;
  } catch {
    return false;
  }
}

export interface UploadResponse {
  status: string;
  message: string;
  document_id?: string;
  chunks_ingested?: number;
  source_file?: string;
  document_type?: string;
  error?: string;
}

/**
 * Upload PDF file to backend
 */
export async function uploadPDF(
  file: File,
  documentType?: string,
  onProgress?: (progress: number) => void
): Promise<{ success: boolean; fileId?: string; error?: string; chunksIngested?: number }> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    if (documentType) {
      formData.append("document_type", documentType);
    }

    // Show initial progress
    if (onProgress) {
      onProgress(10);
    }

    const response = await fetch(`${API_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    // Update progress during processing
    if (onProgress) {
      onProgress(75);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }

    if (onProgress) {
      onProgress(90);
    }

    const data: UploadResponse = await response.json();

    if (onProgress) {
      onProgress(100);
    }

    if (data.status === "error") {
      return {
        success: false,
        error: data.error || "Upload failed",
      };
    }

    return {
      success: true,
      fileId: data.document_id,
      chunksIngested: data.chunks_ingested,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Upload failed",
    };
  }
}

/**
 * Get collection information
 */
export async function getCollectionInfo(): Promise<{
  collection_name: string;
  document_count: number;
  persist_directory: string;
}> {
  const response = await fetch(`${API_URL}/api/collection/info`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

