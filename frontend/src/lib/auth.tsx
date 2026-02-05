"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface User {
  id: string;
  email: string;
  created_at?: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
}

// API Error type
interface ApiError {
  code: string;
  message: string;
}

// Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    isLoading: false, // Start with false so pages render immediately
    isAuthenticated: false,
  });

  // Track if initial session restore has been attempted
  const initialized = useRef(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // Register a new user
  const register = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Required for cross-origin requests with CORS
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        // Try to parse error response
        try {
          const error: ApiError = await response.json();
          throw new Error(error.message || "Registration failed");
        } catch {
          // If JSON parsing fails, use status text
          throw new Error(`Registration failed: ${response.status} ${response.statusText}`);
        }
      }

      // Registration successful, user should now log in
    } catch (error) {
      // Handle network errors (CORS, connection refused, etc.)
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error("Cannot connect to server. Please check if the backend is running.");
      }
      throw error;
    }
  }, []);

  // Login and get tokens
  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // Important for cookies
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        // Try to parse error response
        try {
          const error: ApiError = await response.json();
          throw new Error(error.message || "Login failed");
        } catch {
          // If JSON parsing fails, use status text
          throw new Error(`Login failed: ${response.status} ${response.statusText}`);
        }
      }

      const data = await response.json();

      // Debug: Log the received data
      console.log("[Auth] Login successful, received:", {
        user: data.user,
        hasAccessToken: !!data.access_token,
        tokenLength: data.access_token?.length,
      });

      // Mark as initialized since we now have a session
      initialized.current = true;

      setState({
        user: data.user,
        accessToken: data.access_token,
        isLoading: false,
        isAuthenticated: true,
      });
    } catch (error) {
      // Handle network errors (CORS, connection refused, etc.)
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error("Cannot connect to server. Please check if the backend is running.");
      }
      throw error;
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    // Get current token before clearing state
    setState((prev) => {
      // Fire and forget the server logout
      if (prev.accessToken) {
        fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${prev.accessToken}`,
          },
          credentials: "include",
        }).catch(() => {
          // Ignore errors - local state is already cleared
        });
      }

      // Return cleared state
      return {
        user: null,
        accessToken: null,
        isLoading: false,
        isAuthenticated: false,
      };
    });
  }, []);

  // Refresh the access token using refresh token cookie
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      // Add timeout to prevent hanging if backend is down
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: "POST",
        credentials: "include", // Send cookies
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Refresh failed - only clear if we don't already have a session
        // (protects against race condition with login)
        setState((prev) => {
          if (prev.accessToken && prev.isAuthenticated) {
            // Already have a valid session (probably from login), keep it
            return { ...prev, isLoading: false };
          }
          // No session, clear everything
          return {
            user: null,
            accessToken: null,
            isLoading: false,
            isAuthenticated: false,
          };
        });
        return false;
      }

      const data = await response.json();

      // Fetch user info with new token
      const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      if (userResponse.ok) {
        const user = await userResponse.json();
        setState({
          user,
          accessToken: data.access_token,
          isLoading: false,
          isAuthenticated: true,
        });
        return true;
      }

      // /me failed - only clear if we don't have a session
      setState((prev) => {
        if (prev.accessToken && prev.isAuthenticated) {
          return { ...prev, isLoading: false };
        }
        return {
          user: null,
          accessToken: null,
          isLoading: false,
          isAuthenticated: false,
        };
      });
      return false;
    } catch {
      // Error - only clear if we don't have a session
      setState((prev) => {
        if (prev.accessToken && prev.isAuthenticated) {
          return { ...prev, isLoading: false };
        }
        return {
          user: null,
          accessToken: null,
          isLoading: false,
          isAuthenticated: false,
        };
      });
      return false;
    }
  }, []);

  // Try to restore session on initial page load only
  useEffect(() => {
    // Only run once on initial mount
    if (initialized.current) {
      return;
    }
    initialized.current = true;

    console.log("[Auth] Starting session restore...");

    // Try to restore session from refresh token cookie
    refreshToken()
      .then((success) => {
        console.log("[Auth] Session restore complete, success:", success);
      })
      .catch((err) => {
        console.error("[Auth] Session restore error:", err);
      })
      .finally(() => {
        console.log("[Auth] Setting isInitializing to false");
        setIsInitializing(false);
      });
  }, []); // Empty deps - only run on mount

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
