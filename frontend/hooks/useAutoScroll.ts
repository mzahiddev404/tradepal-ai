/**
 * Custom hook for auto-scrolling to bottom of scroll container
 */
import { useEffect, useRef } from "react";

export function useAutoScroll<T>(dependency: T) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        '[data-radix-scroll-area-viewport]'
      );
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [dependency]);

  return scrollAreaRef;
}

