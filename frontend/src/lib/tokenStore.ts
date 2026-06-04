// Memory-only access token store using closure variable.
// Access token is never persisted to localStorage, sessionStorage, cookies, or IndexedDB.
// It lives only in RAM and is lost on page reload / tab close.
// Refresh token stays in HttpOnly cookie (backend-managed).
let accessToken: string | null = null;

export const getAccessToken = (): string | null => accessToken;

export const setAccessToken = (token: string): void => {
  accessToken = token;
};

export const clearAccessToken = (): void => {
  accessToken = null;
};
