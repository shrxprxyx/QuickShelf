"use client";
import { useApiClient } from "@/lib/api-client";
import { useEffect, useState } from "react";

export default function MePage() {
  const api = useApiClient();
  const [me, setMe] = useState(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get("/api/v1/auth/me")
      .then((res) => setMe(res.data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div style={{ padding: 40 }}>
      <h1>Auth Test</h1>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      <pre>{JSON.stringify(me, null, 2)}</pre>
    </div>
  );
}