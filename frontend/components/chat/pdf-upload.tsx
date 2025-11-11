"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Upload, X, File, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { uploadPDF } from "@/lib/api";

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
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== "application/pdf") {
      return "Only PDF files are allowed";
    }

    // Check file size
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      return `File size must be less than ${maxSizeMB}MB`;
    }

    return null;
  };

  const handleFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => {
      const error = validateFile(file);
      return {
        id: `${Date.now()}-${file.name}`,
        name: file.name,
        size: file.size,
        status: error ? ("error" as const) : ("uploading" as const),
        progress: error ? 0 : 0,
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
  };

  const uploadFile = async (fileId: string, fileList: FileList) => {
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
      // Update progress callback
      const updateProgress = (progress: number) => {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId ? { ...f, progress } : f
          )
        );
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

        // Notify parent
        if (onUploadComplete) {
          const successFiles = files
            .map((f) => (f.id === fileId ? { ...f, status: "success" as const, progress: 100 } : f))
            .filter((f) => f.status === "success");
          onUploadComplete(successFiles);
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
  };

  const removeFile = (fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <Card
        className={cn(
          "border-2 border-dashed p-8 text-center transition-colors",
          isDragging && "border-primary bg-primary/5"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          multiple
          onChange={handleFileInput}
          className="hidden"
        />
        
        <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">Upload PDF Documents</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Drag and drop PDF files here, or click to browse
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          Maximum file size: {maxSizeMB}MB
        </p>
        
        <Button
          className="mt-4"
          onClick={() => fileInputRef.current?.click()}
        >
          Select Files
        </Button>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Uploaded Files</h4>
          {files.map((file) => (
            <Card key={file.id} className="p-4">
              <div className="flex items-start gap-3">
                <File className="h-5 w-5 flex-shrink-0 text-muted-foreground" />
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm font-medium">{file.name}</p>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 flex-shrink-0"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(file.size)}
                  </p>

                  {file.status === "uploading" && (
                    <div className="mt-2">
                      <Progress value={file.progress} className="h-1" />
                      <p className="mt-1 text-xs text-muted-foreground">
                        Uploading... {file.progress}%
                      </p>
                    </div>
                  )}

                  {file.status === "success" && (
                    <Badge variant="default" className="mt-2">
                      Uploaded
                    </Badge>
                  )}

                  {file.status === "error" && (
                    <div className="mt-2 flex items-center gap-1 text-destructive">
                      <AlertCircle className="h-3 w-3" />
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

