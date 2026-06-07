import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import WebApp from "@twa-dev/sdk";
import { getAuthConfig, getMe, loginTelegram, loginTon } from "../api";
import { setAuthToken, type AuthUser } from "../auth";

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  authRequired: boolean;
  isTelegram: boolean;
  loginWithTelegram: () => Promise<void>;
  loginWithTonWallet: (address: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function telegramInitData(): string {
  try {
    WebApp.ready();
    return WebApp.initData;
  } catch {
    return "";
  }
}

export function AuthProvider({ children }: { children: ReactNode }): React.JSX.Element {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [authRequired, setAuthRequired] = useState(true);

  const isTelegram = useMemo(() => Boolean(telegramInitData()), []);

  const refresh = useCallback(async () => {
    const [config, me] = await Promise.all([getAuthConfig(), getMe()]);
    setAuthRequired(config.auth_required);
    if (me.authenticated) {
      setUser(me.user);
    } else {
      setUser(null);
    }
  }, []);

  const loginWithTelegram = useCallback(async () => {
    WebApp.ready();
    WebApp.expand();
    const initData = WebApp.initData;
    if (!initData) {
      throw new Error("Open this app inside Telegram to use Telegram login.");
    }
    const response = await loginTelegram(initData);
    setAuthToken(response.access_token);
    setUser(response.user);
  }, []);

  const loginWithTonWallet = useCallback(async (address: string) => {
    const response = await loginTon(address);
    setAuthToken(response.access_token);
    setUser(response.user);
  }, []);

  const logout = useCallback(() => {
    setAuthToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    void refresh()
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, [refresh]);

  useEffect(() => {
    if (!isTelegram || loading) {
      return;
    }
    if (user) {
      return;
    }
    void loginWithTelegram().catch(() => undefined);
  }, [isTelegram, loading, user, loginWithTelegram]);

  const value = useMemo(
    () => ({
      user,
      loading,
      authRequired,
      isTelegram,
      loginWithTelegram,
      loginWithTonWallet,
      logout,
      refresh,
    }),
    [user, loading, authRequired, isTelegram, loginWithTelegram, loginWithTonWallet, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
