import { authApi } from "../api/client";
import type { RemobsUser } from "../types";

export const authService = {
  async login(username: string, password: string): Promise<string> {
    const response = await authApi.post<{ access_token: string }>("/auth/login", { username, password });
    return response.data.access_token;
  },

  async getMe(): Promise<RemobsUser> {
    const response = await authApi.get<RemobsUser>("/users/me");
    return response.data;
  },
};
