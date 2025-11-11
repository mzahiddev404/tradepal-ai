import { ChatContainer } from "@/components/chat/chat-container";

export default function Home() {
  return (
    <div className="flex min-h-[calc(100vh-3rem)] items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-5xl">
        <ChatContainer />
      </div>
    </div>
  );
}
