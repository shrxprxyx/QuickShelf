"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApiClient } from "@/lib/api-client";
import { useUser } from "@clerk/nextjs";

export default function Home() {
  const router = useRouter();
  const { isLoaded, isSignedIn } = useUser();
  const api = useApiClient();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in");
      return;
    }

    api.get("/api/v1/auth/me").then((res) => {
      const role = res.data.role;
      if (role === "admin" || role === "librarian") {
        router.replace("/dashboard");
      } else {
        router.replace("/browse");
      }
    });
  }, [isLoaded, isSignedIn]);

  return (
    <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">
      Loading...
    </div>
  );
}