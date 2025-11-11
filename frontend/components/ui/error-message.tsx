import { AlertCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ErrorMessageProps {
  title?: string;
  message: string;
  variant?: "inline" | "card";
  className?: string;
}

export function ErrorMessage({
  title = "Error",
  message,
  variant = "inline",
  className,
}: ErrorMessageProps) {
  if (variant === "card") {
    return (
      <div
        className={cn(
          "rounded-lg border-2 border-red-300 bg-red-100 p-4 shadow-md",
          className
        )}
      >
        <div className="flex items-start gap-3">
          <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-red-900 mb-1">{title}</h4>
            <p className="text-sm text-red-800">{message}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-2 text-sm text-red-800 bg-red-100 px-3 py-2 rounded-md border border-red-300",
        className
      )}
    >
      <AlertCircle className="h-4 w-4 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
}

