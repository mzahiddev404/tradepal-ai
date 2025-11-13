import { ChatContainer } from "@/components/chat/chat-container";
import { ErrorBoundary } from "@/components/error-boundary";

export default function Home() {
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
