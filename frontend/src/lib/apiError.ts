import type { ApiError } from "./types";

// Extracts a human-readable message from an unknown thrown value, preferring the
// backend's { error, message } shape, then the JS Error message, then a fallback.
export function extractErrorMessage(error: unknown, fallback: string): string {
  const e = error as { response?: { data?: Partial<ApiError> }; message?: string };
  return e?.response?.data?.message || e?.message || fallback;
}
