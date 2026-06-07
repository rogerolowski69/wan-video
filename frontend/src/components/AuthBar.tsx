import { useEffect, useRef } from "react";
import { TonConnectButton, useTonWallet } from "@tonconnect/ui-react";
import { useAuth } from "../context/AuthContext";
import { userLabel } from "../auth";

export function AuthBar(): React.JSX.Element {
  const { user, loading, authRequired, isTelegram, loginWithTelegram, loginWithTonWallet, logout } =
    useAuth();
  const wallet = useTonWallet();
  const linkedRef = useRef<string | null>(null);

  useEffect(() => {
    const address = wallet?.account?.address;
    if (!address || user?.wallet_address === address) {
      return;
    }
    if (linkedRef.current === address) {
      return;
    }
    linkedRef.current = address;
    void loginWithTonWallet(address).catch(() => {
      linkedRef.current = null;
    });
  }, [wallet?.account?.address, user?.wallet_address, loginWithTonWallet]);

  if (loading) {
    return <span className="text-xs text-zinc-500">…</span>;
  }

  if (user) {
    return (
      <div className="flex items-center gap-2 flex-wrap justify-end">
        <span className="text-xs text-zinc-300 max-w-[140px] truncate">{userLabel(user)}</span>
        {!user.wallet_address ? (
          <div className="ton-connect-btn scale-90 origin-right">
            <TonConnectButton />
          </div>
        ) : null}
        <button
          type="button"
          onClick={logout}
          className="text-xs text-zinc-500 hover:text-zinc-300 px-2 py-1 rounded border border-white/10"
        >
          Log out
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 flex-wrap justify-end">
      {isTelegram ? (
        <button
          type="button"
          onClick={() => void loginWithTelegram()}
          className="text-xs px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 font-medium"
        >
          Telegram login
        </button>
      ) : (
        <button
          type="button"
          onClick={() => void loginWithTelegram().catch(() => undefined)}
          className="text-xs px-3 py-1.5 rounded-lg border border-white/15 text-zinc-400 hover:text-zinc-200"
          title="Open in Telegram for one-tap login"
        >
          Open in Telegram
        </button>
      )}
      <div className="ton-connect-btn scale-90 origin-right">
        <TonConnectButton />
      </div>
      {authRequired ? (
        <span className="text-[10px] text-zinc-500 hidden sm:inline">Login to generate</span>
      ) : null}
    </div>
  );
}

export function LoginGate({ children }: { children: React.ReactNode }): React.JSX.Element {
  const { user, loading, authRequired } = useAuth();

  if (loading) {
    return <p className="text-center text-zinc-500 text-sm py-8">Checking session…</p>;
  }

  if (authRequired && !user) {
    return (
      <section className="rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-8 text-center space-y-4 max-w-lg mx-auto">
        <h2 className="text-lg font-semibold">Sign in to generate</h2>
        <p className="text-sm text-zinc-400">
          Connect with Telegram (in the Mini App) or link a TON wallet, then launch any model.
        </p>
        <AuthBar />
      </section>
    );
  }

  return <>{children}</>;
}
