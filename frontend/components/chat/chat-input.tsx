"use client";

import { useState, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ChevronDown, ChevronUp, Phone, MessageSquare, Terminal, Command } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  suggestions?: string[];
}

export function ChatInput({ onSend, disabled, suggestions }: ChatInputProps) {
  const [input, setInput] = useState("");
  const [isQuickActionsExpanded, setIsQuickActionsExpanded] = useState(true);
  const [showCrisisInfo, setShowCrisisInfo] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

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

  const toggleQuickActions = () => {
    setIsQuickActionsExpanded((prev) => !prev);
  };

  return (
    <div className="space-y-4">
      {/* Crisis Support Button */}
      <div className="flex items-center justify-center">
        <button
          onClick={() => setShowCrisisInfo(!showCrisisInfo)}
          className="text-[10px] font-medium text-[#ff9500] hover:text-[#ffaa33] transition-all flex items-center gap-1.5 px-3 py-1 rounded-full border border-[#ff9500]/20 hover:border-[#ff9500]/40 bg-[#2d1f0f]/20 hover:bg-[#2d1f0f]/40 uppercase tracking-wider"
          type="button"
        >
          <Phone className="h-3 w-3" />
          <span>Crisis Support</span>
          {showCrisisInfo ? (
            <ChevronUp className="h-3 w-3 transition-transform" />
          ) : (
            <ChevronDown className="h-3 w-3 transition-transform" />
          )}
        </button>
      </div>
      {showCrisisInfo && (
        <div className="rounded-lg border border-[#ff9500]/30 bg-[#2d1f0f]/80 p-4 space-y-3 animate-in fade-in slide-in-from-bottom-2 backdrop-blur-md shadow-[0_0_30px_rgba(255,149,0,0.1)]">
          <p className="text-xs text-[#ff9500] font-semibold uppercase tracking-wide">Need immediate help? Free, confidential support available 24/7:</p>
          <div className="flex flex-col sm:flex-row gap-3">
            <a
              href="tel:1-800-273-8255"
              className="flex items-center justify-center gap-2 px-4 py-2.5 text-xs rounded-md border border-[#ff9500]/50 bg-[#2d1f0f] hover:bg-[#3d2f1f] text-[#ff9500] transition-all hover:shadow-[0_0_15px_rgba(255,149,0,0.2)] font-mono"
            >
              <Phone className="h-3 w-3" />
              <span>1-800-273-TALK (8255)</span>
            </a>
            <a
              href="sms:741741"
              className="flex items-center justify-center gap-2 px-4 py-2.5 text-xs rounded-md border border-[#ff9500]/50 bg-[#2d1f0f] hover:bg-[#3d2f1f] text-[#ff9500] transition-all hover:shadow-[0_0_15px_rgba(255,149,0,0.2)] font-mono"
            >
              <MessageSquare className="h-3 w-3" />
              <span>Text "HELLO" to 741741</span>
            </a>
          </div>
        </div>
      )}
      
      {suggestions && suggestions.length > 0 && (
        <div className="space-y-3">
          <button
            onClick={toggleQuickActions}
            className="text-[10px] font-bold text-[#34c759] uppercase tracking-widest flex items-center gap-2 hover:text-[#28a745] transition-colors cursor-pointer group pl-1"
            type="button"
          >
            <Terminal className="h-3 w-3" />
            Quick Commands
            {isQuickActionsExpanded ? (
              <ChevronUp className="h-3 w-3 transition-transform opacity-50 group-hover:opacity-100" />
            ) : (
              <ChevronDown className="h-3 w-3 transition-transform opacity-50 group-hover:opacity-100" />
            )}
          </button>
          {isQuickActionsExpanded && (
            <div className="flex flex-wrap gap-2 animate-in fade-in slide-in-from-top-1">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  disabled={disabled}
                  className="px-3 py-1.5 text-[11px] rounded-sm border border-[#373d41] bg-[#23272c]/50 hover:bg-[#23272c] hover:border-[#34c759] hover:text-[#34c759] text-gray-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap font-mono hover:shadow-[0_0_10px_rgba(52,199,89,0.1)]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
      
      <div className={cn(
        "flex gap-0 relative rounded-lg overflow-hidden border transition-all duration-300",
        isFocused 
          ? "border-[#34c759] shadow-[0_0_20px_rgba(52,199,89,0.15)] bg-[#0f1115]" 
          : "border-[#2d3237] bg-[#131619]"
      )}>
        <div className="pl-3 py-3 flex items-center justify-center text-[#34c759]">
          <span className="font-mono text-sm select-none">{">"}</span>
        </div>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Enter command or query..."
          disabled={disabled}
          className="flex-1 h-12 border-none focus-visible:ring-0 bg-transparent text-[#dcdcdc] placeholder:text-gray-600 font-mono text-sm"
        />
        <div className="pr-2 py-2">
          <Button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            size="icon"
            className={cn(
              "h-8 w-8 rounded-md transition-all duration-300",
              input.trim() 
                ? "bg-[#34c759] text-black hover:bg-[#28a745] shadow-[0_0_10px_rgba(52,199,89,0.3)]" 
                : "bg-[#2d3237] text-gray-500"
            )}
          >
            <Send className="h-3.5 w-3.5" />
            <span className="sr-only">Execute</span>
          </Button>
        </div>
      </div>
      
      {/* Status Bar under input */}
      <div className="flex justify-between px-1">
        <span className="text-[10px] text-gray-600 font-mono uppercase tracking-wider">
          {input.length > 0 ? "INPUT DETECTED" : "AWAITING INPUT"}
        </span>
        <span className="text-[10px] text-gray-600 font-mono">
          {input.length} CHARS
        </span>
      </div>
    </div>
  );
}
