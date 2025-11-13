"use client";

import { useEffect, useState } from "react";
import { Clock } from "lucide-react";

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
        } else if (hours === 15 && minutes >= 30) {
          setStatus("open");
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
    open: { text: "Market Open", color: "text-green-600", bgColor: "bg-green-50", dotColor: "bg-green-500" },
    closed: { text: "Market Closed", color: "text-slate-600", bgColor: "bg-slate-50", dotColor: "bg-slate-400" },
    premarket: { text: "Pre-Market", color: "text-blue-600", bgColor: "bg-blue-50", dotColor: "bg-blue-500" },
    afterhours: { text: "After Hours", color: "text-amber-600", bgColor: "bg-amber-50", dotColor: "bg-amber-500" },
  };

  const config = statusConfig[status];

  const borderColor = status === 'open' ? 'border-green-200' : status === 'premarket' ? 'border-blue-200' : status === 'afterhours' ? 'border-amber-200' : 'border-slate-200';

  return (
    <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${config.bgColor} border ${borderColor}`}>
      <Clock className={`h-3.5 w-3.5 ${config.color}`} />
      <div className="flex items-center gap-2">
        <span className={`text-xs font-semibold ${config.color}`}>{time}</span>
        <div className="flex items-center gap-1.5">
          <div className={`h-1.5 w-1.5 rounded-full ${config.dotColor} animate-pulse`} />
          <span className={`text-xs font-medium ${config.color}`}>{config.text}</span>
        </div>
      </div>
    </div>
  );
}

