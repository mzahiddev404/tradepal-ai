/**
 * API client with retry logic and better error handling
 */
import { API_URL } from "./constants";

interface RequestOptions extends RequestInit {
  retries?: number;
  retryDelay?: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Fetch with retry logic
 */
async function fetchWithRetry(
  url: string,
  options: RequestOptions = {}
): Promise<Response> {
  const { retries = 3, retryDelay = 1000, ...fetchOptions } = options;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, fetchOptions);

      // Retry on server errors (5xx) or network errors
      if (response.status >= 500 && attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }

      return response;
    } catch (error) {
      // Retry on network errors
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }
      throw error;
    }
  }

  throw new Error("Max retries exceeded");
}

/**
 * Make API request with error handling
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  try {
    const response = await fetchWithRetry(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `API error: ${response.status}`;
      try {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.error || errorMessage;
        } else {
          const text = await response.text();
          errorMessage = text || response.statusText || errorMessage;
        }
      } catch {
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiError(errorMessage, response.status, response.statusText);
    }

    // Check if response has content before parsing JSON
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      if (!text || text.trim().length === 0) {
        throw new ApiError(
          "Empty response from server",
          response.status,
          "Empty Response"
        );
      }
      throw new ApiError(
        `Expected JSON but received ${contentType || "unknown"}`,
        response.status,
        "Invalid Content Type"
      );
    }

    const text = await response.text();
    if (!text || text.trim().length === 0) {
      throw new ApiError(
        "Empty response from server",
        response.status,
        "Empty Response"
      );
    }

    let data;
    try {
      data = JSON.parse(text);
    } catch (parseError) {
      throw new ApiError(
        `Failed to parse JSON response: ${parseError instanceof Error ? parseError.message : "Unknown error"}`,
        response.status,
        "JSON Parse Error"
      );
    }

    // Check if response contains an error field
    if (data.error) {
      throw new ApiError(data.error, response.status, response.statusText);
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new ApiError(
        "Network error: Could not connect to server",
        0,
        "Network Error"
      );
    }

    throw new ApiError(
      error instanceof Error ? error.message : "Unknown error occurred",
      0,
      "Unknown Error"
    );
  }
}


