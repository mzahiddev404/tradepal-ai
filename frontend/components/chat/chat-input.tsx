"use client";

import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  suggestions?: string[];
}

export function ChatInput({ onSend, disabled, suggestions }: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput("");
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    // Optionally auto-send, or just fill the input
    // onSend(suggestion);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-4">
      {suggestions && suggestions.length > 0 && (
        <div className="space-y-2.5">
          <p className="text-xs font-semibold text-[#34c759] uppercase tracking-wider flex items-center gap-2">
            <span className="h-1 w-1 rounded-full bg-[#34c759]"></span>
            Quick Actions
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={disabled}
                className="px-3 py-2 text-xs sm:text-sm rounded-md border border-[#373d41] bg-[#23272c] hover:bg-[#2d3237] hover:border-[#34c759] hover:text-[#34c759] text-[#dcdcdc] transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap font-medium"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about SPY patterns, Tesla analysis, trading rules, getting started..."
          disabled={disabled}
          className="flex-1 h-12 text-sm sm:text-base border-[#2d3237] focus:border-[#34c759] focus:ring-[#34c759]/20 bg-[#23272c] text-[#dcdcdc] placeholder:text-[#6a6a6a] shadow-sm"
        />
        <Button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          size="icon"
          className="h-12 w-12 bg-gradient-to-br from-[#34c759] to-[#28a745] hover:from-[#28a745] hover:to-[#1e7e34] border border-[#28a745] text-white disabled:opacity-50 disabled:cursor-not-allowed shrink-0 shadow-lg"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </div>
  );
}












