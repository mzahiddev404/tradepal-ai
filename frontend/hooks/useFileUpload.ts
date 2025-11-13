/**
 * Custom hook for file upload functionality
 */
import { useState, useCallback } from "react";
import { uploadPDF } from "@/lib/api";
import { formatFileSize } from "@/lib/format";

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "success" | "error";
  progress: number;
  error?: string;
}

interface UseFileUploadReturn {
  files: UploadedFile[];
  uploadFile: (file: File) => Promise<void>;
  removeFile: (fileId: string) => void;
  clearFiles: () => void;
}

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export function useFileUpload(
  onUploadComplete?: (files: UploadedFile[]) => void
): UseFileUploadReturn {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const validateFile = useCallback((file: File): string | null => {
    if (file.type !== "application/pdf") {
      return "Only PDF files are allowed";
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      return `File size must be less than ${MAX_FILE_SIZE_MB}MB`;
    }

    return null;
  }, []);

  const uploadFile = useCallback(
    async (file: File) => {
      const error = validateFile(file);
      const fileId = `${Date.now()}-${file.name}`;

      if (error) {
        setFiles((prev) => [
          ...prev,
          {
            id: fileId,
            name: file.name,
            size: file.size,
            status: "error",
            progress: 0,
            error,
          },
        ]);
        return;
      }

      // Add file to list with uploading status
      setFiles((prev) => [
        ...prev,
        {
          id: fileId,
          name: file.name,
          size: file.size,
          status: "uploading",
          progress: 0,
        },
      ]);

      try {
        let lastProgress = 0;
        const updateProgress = (progress: number) => {
          // Only update if progress changed significantly (every 10% or at completion)
          if (progress === 100 || Math.abs(progress - lastProgress) >= 10) {
            lastProgress = progress;
            setFiles((prev) =>
              prev.map((f) => (f.id === fileId ? { ...f, progress } : f))
            );
          }
        };

        const result = await uploadPDF(file, undefined, updateProgress);

        if (result.success) {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    status: "success",
                    progress: 100,
                  }
                : f
            )
          );

          if (onUploadComplete) {
            const successFiles = files
              .filter((f) => f.status === "success")
              .concat({
                id: fileId,
                name: file.name,
                size: file.size,
                status: "success",
                progress: 100,
              });
            onUploadComplete(successFiles);
          }
        } else {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === fileId
                ? {
                    ...f,
                    status: "error",
                    error: result.error || "Upload failed",
                  }
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
                  status: "error",
                  error:
                    error instanceof Error ? error.message : "Upload failed",
                }
              : f
          )
        );
      }
    },
    [validateFile, onUploadComplete, files]
  );

  const removeFile = useCallback((fileId: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  }, []);

  const clearFiles = useCallback(() => {
    setFiles([]);
  }, []);

  return {
    files,
    uploadFile,
    removeFile,
    clearFiles,
  };
}

