"use client";

import { useState, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Upload, X, File, AlertCircle, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { uploadPDF, clearKnowledgeBase } from "@/lib/api";
import { formatFileSize } from "@/lib/format";

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "success" | "error";
  progress: number;
  error?: string;
}

interface PDFUploadProps {
  onUploadComplete?: (files: UploadedFile[]) => void;
  maxSizeMB?: number;
}

export function PDFUpload({ onUploadComplete, maxSizeMB = 10 }: PDFUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [shouldReplace, setShouldReplace] = useState(true); // Default to replace for better UX
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClearKnowledgeBase = async () => {
    if (!confirm("Are you sure you want to delete all documents from the Knowledge Base? This action cannot be undone.")) {
      return;
    }
    
    setIsClearing(true);
    try {
      await clearKnowledgeBase();
      setFiles([]); // Clear local file list
      alert("Knowledge Base cleared successfully.");
    } catch (error) {
      alert(`Failed to clear Knowledge Base: ${error instanceof Error ? error.message : "Unknown error"}`);
    } finally {
      setIsClearing(false);
    }
  };

  const validateFile = useCallback((file: File): string | null => {
    // Allow PDF or CSV
    const allowedTypes = ["application/pdf", "text/csv", "application/vnd.ms-excel"]; // ms-excel sometimes used for CSV
    const isCSV = file.name.toLowerCase().endsWith('.csv');
    
    if (!allowedTypes.includes(file.type) && !isCSV) {
      return "Only PDF or CSV files are allowed";
    }

    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      return `File size must be less than ${maxSizeMB}MB`;
    }

    return null;
  }, [maxSizeMB]);

  const uploadFile = useCallback(async (fileId: string, fileList: FileList) => {
    const file = Array.from(fileList).find((f) => {
      const fileIdParts = fileId.split("-");
      const fileName = fileIdParts.slice(1).join("-");
      return f.name === fileName;
    });
    
    if (!file) {
      // Try to find by matching the file name pattern
      const matchingFile = Array.from(fileList).find((f) => 
        fileId.includes(f.name)
      );
      if (!matchingFile) return;
      
      return uploadFile(fileId, { 
        0: matchingFile, 
        length: 1, 
        item: () => matchingFile,
        [Symbol.iterator]: function* () { yield matchingFile; }
      } as FileList);
    }

    try {
      // Update progress callback - optimize to reduce re-renders
      let lastProgress = 0;
      const updateProgress = (progress: number) => {
        // Only update if progress changed significantly (every 10% or at completion)
        if (progress === 100 || Math.abs(progress - lastProgress) >= 10) {
          lastProgress = progress;
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId ? { ...f, progress } : f
            )
          );
        }
      };

      // Upload to backend
      const result = await uploadPDF(file, undefined, updateProgress);

      if (result.success) {
        // Mark as success
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? {
                  ...f,
                  status: "success" as const,
                  progress: 100,
                }
              : f
          )
        );

        // Notify parent with current state
        if (onUploadComplete) {
          setFiles((currentFiles) => {
            const successFiles = currentFiles
              .filter((f) => f.status === "success")
              .map((f) => (f.id === fileId ? { ...f, status: "success" as const, progress: 100 } : f));
            onUploadComplete(successFiles);
            return currentFiles;
          });
        }
      } else {
        // Mark as error
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId
              ? { ...f, status: "error" as const, error: result.error || "Upload failed" }
              : f
          )
        );
      }
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === fileId
            ? {
                ...f,
                status: "error" as const,
                error: error instanceof Error ? error.message : "Upload failed",
              }
            : f
        )
      );
    }
  }, [onUploadComplete]);

  const handleFiles = useCallback(async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    // If Replace Mode is active, clear KB first
    if (shouldReplace) {
        try {
            setIsClearing(true);
            await clearKnowledgeBase();
            setFiles([]); // Clear previous list from UI
        } catch (e) {
            console.error("Failed to clear KB before upload", e);
            // Continue anyway? Or stop? Let's continue but warn.
        } finally {
            setIsClearing(false);
        }
    }

    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => {
      const error = validateFile(file);
      return {
        id: `${Date.now()}-${file.name}`,
        name: file.name,
        size: file.size,
        status: error ? ("error" as const) : ("uploading" as const),
        progress: 0,
        error: error || undefined,
      };
    });

    setFiles((prev) => [...prev, ...newFiles]);

    // Upload valid files
    for (const fileData of newFiles) {
      if (fileData.status === "uploading") {
        await uploadFile(fileData.id, fileList);
      }
    }
  }, [validateFile, uploadFile, shouldReplace]);

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);


  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card
        className={cn(
          "border-2 border-dashed border-[#2d3237] p-8 sm:p-10 text-center transition-colors bg-[#1a1e23]/95 backdrop-blur-sm",
          isDragging && "border-[#34c759] bg-[#1a2e1a]/30"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.csv"
          multiple
          onChange={handleFileInput}
          className="hidden"
          aria-label="Upload PDF or CSV files"
        />

        <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-[#34c759] to-[#28a745] flex items-center justify-center shadow-lg border-2 border-[#28a745]">
          <Upload className="h-8 w-8 text-white" aria-hidden="true" />
        </div>
        <h3 className="mt-4 text-base font-bold text-[#dcdcdc] font-mono uppercase tracking-wide">Upload Documents</h3>
        <p className="mt-2 text-sm text-[#9ca3af]">
          Drag and drop PDF or CSV files here, or click to browse
        </p>
        <p className="mt-1 text-xs text-[#6a6a6a]">
          Maximum file size: {maxSizeMB}MB
        </p>

        <Button 
          className="mt-5 h-9 bg-gradient-to-br from-[#34c759] to-[#28a745] hover:from-[#28a745] hover:to-[#1e7e34] border border-[#28a745] text-white shadow-md transition-all hover:shadow-lg" 
          onClick={() => fileInputRef.current?.click()}
        >
          Select Files
        </Button>

        <div className="mt-6 p-3 bg-blue-900/10 border border-blue-500/20 rounded text-xs text-left flex gap-2 items-start">
          <AlertCircle className="h-4 w-4 text-blue-400 flex-shrink-0 mt-0.5" />
          <p className="text-blue-300/80 leading-relaxed">
            <strong className="text-blue-400 font-medium">Tip:</strong> After uploading PDFs/CSVs, you can ask questions about their content in the chat or run Smart Flow Analysis. The AI will retrieve relevant signals from your documents.
          </p>
        </div>
      </Card>

      {/* Controls Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
            <input 
                type="checkbox" 
                id="replace-kb" 
                checked={shouldReplace} 
                onChange={(e) => setShouldReplace(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-[#34c759] focus:ring-[#34c759] bg-[#23272c] border-[#2d3237]"
            />
            <label htmlFor="replace-kb" className="text-xs text-gray-400 cursor-pointer select-none">
                Replace existing Knowledge Base (Fresh Analysis)
            </label>
        </div>

        <Button
          variant="outline"
          size="sm"
          className="text-xs text-red-400 border-red-500/20 hover:bg-red-500/10 hover:text-red-300"
          onClick={handleClearKnowledgeBase}
          disabled={isClearing}
        >
          <Trash2 className="h-3.5 w-3.5 mr-2" />
          {isClearing ? "Clearing..." : "Clear Knowledge Base"}
        </Button>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-[#dcdcdc]">Uploaded Files</h4>
          {files.map((file) => (
            <Card key={file.id} className="p-4 border-[#2d3237] bg-[#23272c]">
              <div className="flex items-start gap-3">
                <File className="h-5 w-5 flex-shrink-0 text-[#6a6a6a]" aria-hidden="true" />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm font-medium text-[#dcdcdc]">{file.name}</p>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7 flex-shrink-0 hover:bg-[#32363a]"
                      onClick={() => removeFile(file.id)}
                      aria-label={`Remove ${file.name}`}
                    >
                      <X className="h-4 w-4 text-[#9ca3af] hover:text-[#ff3b30]" />
                    </Button>
                  </div>

                  <p className="text-xs text-[#9ca3af] mt-0.5">
                    {formatFileSize(file.size)}
                  </p>

                  {file.status === "uploading" && (
                    <div className="mt-3">
                      <Progress value={file.progress} className="h-1.5" />
                      <p className="mt-1.5 text-xs text-[#9ca3af]">
                        Uploading... {file.progress}%
                      </p>
                    </div>
                  )}

                  {file.status === "success" && (
                    <div className="mt-3 grid grid-cols-3 gap-2 text-[9px] font-mono uppercase tracking-wider">
                      <div className="bg-[#1a2e1a] border border-[#34c759]/30 p-2 rounded flex flex-col items-center text-center">
                        <span className="text-[#34c759] font-bold mb-1">STATUS</span>
                        <span className="text-[#dcdcdc]">ACTIVE</span>
                      </div>
                      <div className="bg-blue-900/10 border border-blue-500/30 p-2 rounded flex flex-col items-center text-center">
                        <span className="text-blue-400 font-bold mb-1">STORAGE</span>
                        <span className="text-[#dcdcdc]">PERSISTENT</span>
                      </div>
                      <div className="bg-black/20 border border-white/5 p-2 rounded flex flex-col items-center text-center">
                        <span className="text-gray-500 font-bold mb-1">SCOPE</span>
                        <span className="text-[#dcdcdc]">CHAT + FLOW</span>
                      </div>
                    </div>
                  )}

                  {file.status === "error" && (
                    <div className="mt-2 flex items-center gap-1.5 text-[#ff6b6b]">
                      <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
                      <p className="text-xs">{file.error}</p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

