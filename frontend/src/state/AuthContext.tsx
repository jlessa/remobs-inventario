import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { authService } from "../services/authService";
import type { RemobsUser } from "../types";

interface AuthContextValue {
  token: string | null;
  user: RemobsUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("remobs_token"));
  const [user, setUser] = useState<RemobsUser | null>(null);
  const [loading, setLoading] = useState(Boolean(token));

  const refreshUser = useCallback(async () => {
    if (!localStorage.getItem("remobs_token")) {
      setUser(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const currentUser = await authService.getMe();
      setUser(currentUser);
    } finally {
      setLoading(false);
    }
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      const newToken = await authService.login(username, password);
      localStorage.setItem("remobs_token", newToken);
      setToken(newToken);
      await refreshUser();
    },
    [refreshUser],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("remobs_token");
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (token) {
      refreshUser().catch(() => {
        localStorage.removeItem("remobs_token");
        setToken(null);
        setUser(null);
        setLoading(false);
      });
    }
  }, [refreshUser, token]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      loading,
      login,
      logout,
      refreshUser,
      hasPermission: (permission: string) =>
        Boolean(user?.permission_codes.includes("*") || user?.permission_codes.includes(permission)),
    }),
    [loading, login, logout, refreshUser, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return context;
}
