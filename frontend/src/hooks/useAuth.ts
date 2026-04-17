import { useMemo } from "react";
import { clearToken, getToken, setToken } from "../services/auth";

export function useAuth() {
  return useMemo(
    () => ({
      isAuthenticated: Boolean(getToken()),
      login: (token: string) => setToken(token),
      logout: () => clearToken(),
    }),
    []
  );
}
