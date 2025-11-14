import { ChatContainer } from "@/components/chat/chat-container";
import { ErrorBoundary } from "@/components/error-boundary";
<<<<<<< HEAD

export default function Home() {
=======
import { AppHeader } from "@/components/layout/app-header";
import { useState } from "react";
import { useRouter } from "next/navigation";

type ChatMode = "standard" | "multi-llm";

export default function Home() {
  const router = useRouter();
  const [chatMode, setChatMode] = useState<ChatMode>("standard");
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (mode: ChatMode) => {
    if (mode === "multi-llm") {
      // Navigate to compare page
      router.push("/compare");
    } else {
      // Already on standard page, just update state
      setChatMode(mode);
      setShowUpload(false);
      setError(null);
    }
  };

  const handleToggleUpload = () => {
    setShowUpload((prev) => !prev);
    setError(null);
  };

>>>>>>> 8e1eab7 (Add news feed to Compare Chat and improve Standard Chat error handling)
  return (
    <div className="flex min-h-screen items-center justify-center p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-6xl">
        <ErrorBoundary>
          <ChatContainer />
        </ErrorBoundary>
      </div>
    </div>
  );
}
