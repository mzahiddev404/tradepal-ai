/**
 * Document upload view component
 * Handles PDF upload interface
 */
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { PDFUpload } from "./pdf-upload";

interface UploadViewProps {
  onReturnToChat: () => void;
}

export function UploadView({ onReturnToChat }: UploadViewProps) {
  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-[#1a1e23] to-[#141820]">
      <div className="flex-shrink-0 p-4 border-b border-[#2d3237] bg-gradient-to-b from-[#23272c] to-[#1a1e23]">
        <Button
          variant="outline"
          onClick={onReturnToChat}
          className="h-9 border-[#2d3237] text-[#dcdcdc] hover:bg-[#32363a] hover:border-[#34c759] hover:text-[#34c759] transition-colors"
          aria-label="Return to chat"
        >
          ← Back to Chat
        </Button>
      </div>
      <ScrollArea className="flex-1 p-4 sm:p-6 lg:p-8">
        <PDFUpload
          onUploadComplete={(files) => {
            console.log("Files uploaded:", files);
          }}
        />
        <div className="mt-6 p-4 bg-[#1a2e1a] border border-[#34c759]/30 rounded-lg">
          <p className="text-sm text-[#9ca3af]">
            <span className="font-medium text-[#34c759]">Tip:</span> After uploading PDFs, ask questions about their content in the chat. The AI will retrieve relevant information from your documents.
          </p>
        </div>
      </ScrollArea>
    </div>
  );
}

