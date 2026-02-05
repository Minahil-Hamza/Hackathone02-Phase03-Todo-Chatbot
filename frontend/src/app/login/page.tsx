"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { AuthForm } from "@/components/AuthForm";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Redirect if already authenticated (after auth check completes)
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, authLoading, router]);

  const handleLogin = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      await login(email, password);
      // Redirect will happen via useEffect when isAuthenticated changes
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  // Show the form immediately - don't wait for auth check
  return (
    <AuthForm mode="login" onSubmit={handleLogin} isLoading={isLoading} />
  );
}
