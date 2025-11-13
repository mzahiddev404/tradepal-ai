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
    <div className="flex flex-col h-full bg-gradient-to-b from-slate-50 to-white">
      <div className="flex-shrink-0 p-4 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white">
        <Button
          variant="outline"
          onClick={onReturnToChat}
          className="h-9 border-slate-300 text-slate-700 hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 transition-colors"
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
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900">
            <span className="font-medium">Tip:</span> After uploading PDFs, ask questions about their content in the chat. The AI will retrieve relevant information from your documents.
          </p>
        </div>
      </ScrollArea>
    </div>
  );
}

