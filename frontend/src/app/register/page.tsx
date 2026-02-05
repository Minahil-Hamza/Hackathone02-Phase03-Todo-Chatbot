"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { AuthForm } from "@/components/AuthForm";

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    console.log("[Register] Page mounted");
  }, []);

  const handleRegister = async (email: string, password: string) => {
    console.log("[Register] Submitting registration...");
    setIsLoading(true);
    try {
      await register(email, password);
      console.log("[Register] Success, redirecting to login");
      router.push("/login?registered=true");
    } catch (error) {
      console.error("[Register] Error:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  console.log("[Register] Rendering form");
  return <AuthForm mode="register" onSubmit={handleRegister} isLoading={isLoading} />;
}
