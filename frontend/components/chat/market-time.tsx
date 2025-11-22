"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";

export function MarketTime() {
  const [time, setTime] = useState<string>("");
  const [status, setStatus] = useState<"open" | "closed" | "premarket" | "afterhours">("closed");

  useEffect(() => {
    const updateTime = () => {
      // Get current time in Eastern Time
      const now = new Date();
      const estTime = new Date(now.toLocaleString("en-US", { timeZone: "America/New_York" }));
      
      // Format time
      const hours = estTime.getHours();
      const minutes = estTime.getMinutes();
      const seconds = estTime.getSeconds();
      const ampm = hours >= 12 ? "PM" : "AM";
      const displayHours = hours % 12 || 12;
      
      setTime(`${displayHours}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")} ${ampm} ET`);
      
      // Determine market status
      const day = estTime.getDay();
      const isWeekend = day === 0 || day === 6;
      
      if (isWeekend) {
        setStatus("closed");
      } else if (hours >= 9 && hours < 16) {
        if (hours === 9 && minutes < 30) {
          setStatus("premarket");
        } else {
          setStatus("open");
        }
      } else if (hours >= 4 && hours < 9) {
        setStatus("premarket");
      } else if (hours >= 16 && hours < 20) {
        setStatus("afterhours");
      } else {
        setStatus("closed");
      }
    };

    // Update immediately
    updateTime();
    
    // Update every second
    const interval = setInterval(updateTime, 1000);
    
    return () => clearInterval(interval);
  }, []);

  const statusConfig = {
    open: { 
      text: "Market Open", 
      color: "text-[#34c759]", 
      bgColor: "bg-[#34c759]/10", 
      borderColor: "border-[#34c759]/20",
      dotColor: "bg-[#34c759]" 
    },
    closed: { 
      text: "Market Closed", 
      color: "text-[#ff3b30]", 
      bgColor: "bg-[#ff3b30]/10", 
      borderColor: "border-[#ff3b30]/20",
      dotColor: "bg-[#ff3b30]" 
    },
    premarket: { 
      text: "Pre-Market", 
      color: "text-[#ff9500]", 
      bgColor: "bg-[#ff9500]/10", 
      borderColor: "border-[#ff9500]/20",
      dotColor: "bg-[#ff9500]" 
    },
    afterhours: { 
      text: "After Hours", 
      color: "text-[#ff9500]", 
      bgColor: "bg-[#ff9500]/10", 
      borderColor: "border-[#ff9500]/20",
      dotColor: "bg-[#ff9500]" 
    },
  };

  const config = statusConfig[status];

  return (
    <div className={cn(
      "flex items-center gap-2 px-3 py-1.5 rounded border font-mono transition-colors",
      config.bgColor,
      config.borderColor
    )}>
      <Clock className={cn("h-3.5 w-3.5", config.color)} />
      <div className="flex items-center gap-2">
        <span className={cn("text-xs font-bold", config.color)}>{time}</span>
        <div className="hidden sm:flex items-center gap-1.5 border-l border-white/10 pl-2">
          <div className={cn("h-1.5 w-1.5 rounded-full animate-pulse", config.dotColor)} />
          <span className={cn("text-[10px] font-bold uppercase tracking-wider", config.color)}>{config.text}</span>
        </div>
      </div>
    </div>
  );
}
