"use client";

import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { motion } from "framer-motion";
import {
  Upload,
  FileText,
  AlertCircle,
  CheckCircle,
  X,
  RotateCcw,
} from "lucide-react";
import toast from "react-hot-toast";
import axios from "axios";
import FileSizeHelper from "./FileSizeHelper";
import ValidationErrors from "./ValidationErrors";
import { useErrorManager } from "../../hooks/useErrorManager";

interface FileUploadProps {
  onComplete: (data: any) => void;
}

export default function FileUpload({ onComplete }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "completed" | "error" | "cancelled"
  >("idle");
  const [error, setError] = useState<string | null>(null);
  const [showSizeHelper, setShowSizeHelper] = useState(false);
  const [rejectedFile, setRejectedFile] = useState<File | null>(null);
  const [validationErrors, setValidationErrors] = useState<any[]>([]);
  const [validationWarnings, setValidationWarnings] = useState<any[]>([]);
  const [showValidation, setShowValidation] = useState(false);
  const { addError } = useErrorManager();

  // Test backend connectivity
  const testBackendConnection = async () => {
    try {
      console.log('🔍 Testing backend connection...');
      const response = await axios.get('http://localhost:8000/', { timeout: 5000 });
      console.log('✅ Backend connection successful:', response.data);
      toast.success('Backend is connected!');
      return true;
    } catch (error: any) {
      console.error('❌ Backend connection failed:', error);
      toast.error('Cannot connect to backend server');
      return false;
    }
  };

  // Poll upload status
  useEffect(() => {
    if (
      !uploadId ||
      uploadStatus === "completed" ||
      uploadStatus === "error" ||
      uploadStatus === "cancelled"
    ) {
      return;
    }

    const pollStatus = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/upload/${uploadId}/status`
        );
        const status = response.data;

        setUploadProgress(status.progress);
        setUploadStatus(status.status);

        if (status.status === "uploaded") {
          setUploadStatus("completed");
          setIsUploading(false);
          toast.success("File uploaded successfully!");
          onComplete({
            upload_id: uploadId,
            filename: status.filename,
            file_size: status.file_size,
            upload_time: new Date(),
            status: "uploaded",
          });
        } else if (status.status === "error") {
          setUploadStatus("error");
          setError(status.error || "Upload failed");
          setIsUploading(false);
          toast.error(status.error || "Upload failed");
        }
      } catch (error) {
        console.error("Status polling error:", error);
        setUploadStatus("error");
        setError("Failed to check upload status");
        setIsUploading(false);
      }
    };

    const interval = setInterval(pollStatus, 1000); // Poll every second
    return () => clearInterval(interval);
  }, [uploadId, uploadStatus, onComplete]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      // Check file size (1GB limit)
      const maxSize = 1024 * 1024 * 1024; // 1GB
      if (file.size > maxSize) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(0);

        setUploadStatus("error");
        setError(
          `File too large: ${fileSizeMB}MB. Maximum size is ${maxSizeMB}MB.`
        );
        setRejectedFile(file);
        setShowSizeHelper(true);
        toast.error(
          `File too large: ${fileSizeMB}MB. Maximum size is ${maxSizeMB}MB.`
        );
        return;
      }

      // If there's an existing upload, replace it
      if (uploadId && uploadStatus === "uploading") {
        await cancelUpload();
      }

      setUploadedFile(file);
      setIsUploading(true);
      setUploadStatus("uploading");
      setUploadProgress(0);
      setError(null);
      setValidationErrors([]);
      setValidationWarnings([]);
      setShowValidation(false);

      try {
        // Skip validation for debugging - go directly to upload
        console.log('🚀 Starting direct upload...');
        
        const formData = new FormData();
        formData.append("file", file);

        // Proceed with upload
        const uploadResponse = await axios.post(
          "http://localhost:8000/upload",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        console.log('✅ Upload response:', uploadResponse.data);
        setUploadId(uploadResponse.data.upload_id);
        toast.success("Upload started!");
      } catch (error: any) {
        console.error("Upload error:", error);
        console.error("Error details:", {
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
          code: error.code
        });
        setUploadStatus("error");

        let errorMessage = "Failed to start upload";
        let errorDetails = "";

        if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
          errorMessage = "Cannot connect to server";
          errorDetails = "Please ensure the backend is running on http://localhost:8000";
        } else if (error.response?.status === 413) {
          errorMessage = "File too large";
          errorDetails = "The file exceeds the maximum size limit of 1GB";
        } else if (error.response?.status === 415) {
          errorMessage = "Unsupported file type";
          errorDetails = "Please upload CSV, Excel, or JSON files only";
        } else if (error.response?.status === 500) {
          errorMessage = "Server error";
          errorDetails =
            "Please try again or contact support if the issue persists";
        } else if (error.code === "NETWORK_ERROR") {
          errorMessage = "Network error";
          errorDetails = "Please check your internet connection and try again";
        } else if (error.response?.data?.message) {
          errorMessage = error.response.data.message;
          errorDetails = error.response.data.detail || "";
        }

        setError(errorMessage);
        setIsUploading(false);

        // Add to error manager
        addError(errorMessage, "error", errorDetails, {
          label: "Try Again",
          onClick: () => {
            setUploadStatus("idle");
            setError(null);
            setUploadedFile(null);
            setUploadId(null);
            setUploadProgress(0);
          },
        });

        toast.error(errorMessage);
      }
    },
    [uploadId, uploadStatus]
  );

  const cancelUpload = async () => {
    if (!uploadId) return;

    try {
      await axios.delete(`http://localhost:8000/upload/${uploadId}`);
      setUploadStatus("cancelled");
      setIsUploading(false);
      setUploadProgress(0);
      toast("Upload cancelled", { icon: "ℹ️" });
    } catch (error) {
      console.error("Cancel upload error:", error);
      toast.error("Failed to cancel upload");
    }
  };

  const replaceUpload = async (file: File) => {
    if (!uploadId) return;

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(
        `http://localhost:8000/upload/${uploadId}/replace`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setUploadId(response.data.upload_id);
      setUploadedFile(file);
      setUploadStatus("uploading");
      setUploadProgress(0);
      setError(null);
      toast.success("File replaced successfully!");
    } catch (error: any) {
      console.error("Replace upload error:", error);
      setError(error.response?.data?.message || "Failed to replace file");
      toast.error(error.response?.data?.message || "Failed to replace file");
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/csv": [".csv"],
      "application/vnd.ms-excel": [".xls"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
      "application/json": [".json"],
    },
    multiple: false,
  });

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Upload Your Data</h2>
        <p className="text-gray-600">
          Drag and drop your file or click to browse. We support CSV, Excel, and
          JSON formats.
        </p>
        {/* Backend connectivity test button */}
        <div className="mt-4">
          <button
            onClick={testBackendConnection}
            className="px-4 py-2 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
          >
            🔍 Test Backend Connection
          </button>
        </div>
      </div>

      <motion.div
        {...(getRootProps() as any)}
        className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300
          ${
            isDragActive
              ? "border-primary-500 bg-primary-50 dark:bg-primary-900/20"
              : "border-gray-300 dark:border-gray-600 hover:border-primary-400 hover:bg-gray-50 dark:hover:bg-gray-800"
          }
          ${isUploading ? "pointer-events-none opacity-50" : ""}
        `}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <input {...getInputProps()} />

        {uploadStatus === "uploading" ? (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">Uploading...</p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-1">
                {Math.round(uploadProgress)}%
              </p>
            </div>
            <button
              onClick={cancelUpload}
              className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors mx-auto"
            >
              <X className="w-4 h-4" />
              <span>Cancel Upload</span>
            </button>
          </div>
        ) : uploadStatus === "completed" ? (
          <div className="space-y-4">
            <CheckCircle className="w-16 h-16 mx-auto text-success-600" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-900">
                {uploadedFile?.name}
              </p>
              <p className="text-sm text-gray-600">
                {(uploadedFile?.size! / 1024 / 1024).toFixed(2)} MB
              </p>
              <p className="text-sm text-success-600 mt-2">
                ✓ Upload completed
              </p>
            </div>
            <button
              onClick={() => {
                setUploadedFile(null);
                setUploadId(null);
                setUploadStatus("idle");
                setUploadProgress(0);
                setError(null);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors mx-auto"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Upload New File</span>
            </button>
          </div>
        ) : uploadStatus === "error" ? (
          <div className="space-y-4">
            <AlertCircle className="w-16 h-16 mx-auto text-red-600" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-900">Upload Failed</p>
              <p className="text-sm text-red-600 mt-2">{error}</p>
            </div>
            <div className="flex space-x-3 justify-center">
              {error?.includes("too large") && (
                <button
                  onClick={() => setShowSizeHelper(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>Get Help</span>
                </button>
              )}
              <button
                onClick={() => {
                  setUploadedFile(null);
                  setUploadId(null);
                  setUploadStatus("idle");
                  setUploadProgress(0);
                  setError(null);
                }}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Try Again</span>
              </button>
            </div>
          </div>
        ) : uploadStatus === "cancelled" ? (
          <div className="space-y-4">
            <X className="w-16 h-16 mx-auto text-gray-400" />
            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">
                Upload Cancelled
              </p>
              <p className="text-sm text-gray-500 mt-2">
                You can start a new upload
              </p>
            </div>
            <button
              onClick={() => {
                setUploadedFile(null);
                setUploadId(null);
                setUploadStatus("idle");
                setUploadProgress(0);
                setError(null);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors mx-auto"
            >
              <Upload className="w-4 h-4" />
              <span>Start New Upload</span>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="w-16 h-16 mx-auto text-gray-400" />
            <div>
              <p className="text-lg font-medium text-gray-700">
                {isDragActive
                  ? "Drop your file here"
                  : "Choose a file or drag it here"}
              </p>
              <p className="text-sm text-gray-500 mt-2">
                CSV, Excel (.xlsx, .xls), or JSON files
              </p>
            </div>
          </div>
        )}
      </motion.div>

      {/* File Requirements */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-800 dark:text-blue-200">
            <p className="font-medium mb-1">File Requirements:</p>
            <ul className="space-y-1 text-blue-700 dark:text-blue-300">
              <li>
                • <strong>Maximum file size: 1GB</strong> (larger files will be
                rejected)
              </li>
              <li>• Supported formats: CSV, Excel (.xlsx, .xls), JSON</li>
              <li>• First row should contain column headers</li>
              <li>• UTF-8 encoding recommended</li>
            </ul>
            <div className="mt-2 p-2 bg-yellow-100 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-lg">
              <p className="text-xs text-yellow-800 dark:text-yellow-200">
                <strong>Large files:</strong> Files over 100MB will use
                optimized chunked processing for better performance.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Supported Formats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { format: "CSV", description: "Comma-separated values", icon: "📊" },
          { format: "Excel", description: "Spreadsheet files", icon: "📈" },
          {
            format: "JSON",
            description: "JavaScript Object Notation",
            icon: "📋",
          },
        ].map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
          >
            <span className="text-2xl">{item.icon}</span>
            <div>
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {item.format}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {item.description}
              </p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Validation Errors Display */}
      {showValidation &&
        (validationErrors.length > 0 || validationWarnings.length > 0) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
          >
            <ValidationErrors
              errors={validationErrors}
              warnings={validationWarnings}
              onDismiss={() => {
                setShowValidation(false);
                setValidationErrors([]);
                setValidationWarnings([]);
              }}
              onRetry={() => {
                setShowValidation(false);
                setValidationErrors([]);
                setValidationWarnings([]);
                setError(null);
                setUploadStatus("idle");
              }}
            />
          </motion.div>
        )}

      {/* File Size Helper Modal */}
      {showSizeHelper && rejectedFile && (
        <FileSizeHelper
          fileSize={rejectedFile.size}
          maxSize={1024 * 1024 * 1024} // 1GB
          onClose={() => {
            setShowSizeHelper(false);
            setRejectedFile(null);
            setUploadStatus("idle");
            setError(null);
          }}
        />
      )}
    </div>
  );
}
