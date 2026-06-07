export type AuthUser = {
  id: number;
  telegram_id: number | null;
  wallet_address: string | null;
  username: string | null;
  display_name: string | null;
  photo_url: string | null;
};

export type AuthConfig = {
  auth_required: boolean;
  telegram_enabled: boolean;
  ton_enabled: boolean;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type MeResponse =
  | { authenticated: false; auth_required: boolean }
  | { authenticated: true; auth_required: boolean; user: AuthUser };

const TOKEN_KEY = "wan_video_token";

let authToken: string | null =
  typeof localStorage !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;

export function getAuthToken(): string | null {
  return authToken;
}

export function setAuthToken(token: string | null): void {
  authToken = token;
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function authHeaders(): Record<string, string> {
  if (!authToken) {
    return {};
  }
  return { Authorization: `Bearer ${authToken}` };
}

export function userLabel(user: AuthUser): string {
  if (user.display_name) {
    return user.display_name;
  }
  if (user.username) {
    return `@${user.username}`;
  }
  if (user.wallet_address) {
    const w = user.wallet_address;
    return `${w.slice(0, 4)}…${w.slice(-4)}`;
  }
  return `User #${user.id}`;
}
