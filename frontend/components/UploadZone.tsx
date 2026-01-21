"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, File, X, CheckCircle, AlertCircle, Youtube } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface UploadZoneProps {
  onComplete?: () => void;
}

export function UploadZone({ onComplete }: UploadZoneProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  // Form data
  const [projectName, setProjectName] = useState("");
  const [courseName, setCourseName] = useState("");
  const [moduleName, setModuleName] = useState("");
  const [lectureName, setLectureName] = useState("");
  const [description, setDescription] = useState("");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
      'application/pdf': ['.pdf'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.ogg'],
      'video/*': ['.mp4', '.webm', '.mov'],
      'text/*': ['.txt', '.md'],
      'application/zip': ['.zip'],
      'text/x-python': ['.py'],
      'text/javascript': ['.js'],
      'text/typescript': ['.ts'],
      'text/x-solidity': ['.sol'],
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0 && !youtubeUrl) {
      toast.error("Please add files or YouTube URL");
      return;
    }

    setUploading(true);
    setProgress(0);

    try {
      const formData = new FormData();
      
      // Add files
      files.forEach((file) => {
        formData.append("files", file);
      });

      // Add metadata
      if (projectName) formData.append("project_name", projectName);
      if (courseName) formData.append("course_name", courseName);
      if (moduleName) formData.append("module_name", moduleName);
      if (lectureName) formData.append("lecture_name", lectureName);
      if (description) formData.append("description", description);
      if (youtubeUrl) formData.append("url", youtubeUrl);

      // Upload with progress
      const response = await api.post("/upload", formData, {
        //@ts-ignore
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 100)
          );
          setProgress(percentCompleted);
        },
      });

      toast.success("Upload successful! Processing started...");
      
      // Reset form
      setFiles([]);
      setYoutubeUrl("");
      setProjectName("");
      setCourseName("");
      setModuleName("");
      setLectureName("");
      setDescription("");
      
      onComplete?.();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="space-y-6">
      {/* Project Info Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          placeholder="Project Name (optional)"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
        />
        <Input
          placeholder="Course Name (e.g., blockchain-101)"
          value={courseName}
          onChange={(e) => setCourseName(e.target.value)}
        />
        <Input
          placeholder="Module (e.g., mod-1)"
          value={moduleName}
          onChange={(e) => setModuleName(e.target.value)}
        />
        <Input
          placeholder="Lecture (e.g., lec-4)"
          value={lectureName}
          onChange={(e) => setLectureName(e.target.value)}
        />
        <Input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="md:col-span-2"
        />
      </div>

      {/* Drag & Drop Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? "border-vintage-yellow bg-vintage-yellow/10" 
            : "border-border hover:border-vintage-yellow/50"
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-lg font-medium mb-2">
          {isDragActive ? "Drop files here..." : "Drag & drop files here"}
        </p>
        <p className="text-sm text-muted-foreground">
          or click to browse
        </p>
        <p className="text-xs text-muted-foreground mt-2">
          Supports: Images, PDFs, Audio, Video, Code, ZIP (max 50MB)
        </p>
      </div>

      {/* YouTube URL Input */}
      <div className="flex items-center gap-2">
        <Youtube className="h-5 w-5 text-red-500" />
        <Input
          placeholder="Or paste YouTube URL here..."
          value={youtubeUrl}
          onChange={(e) => setYoutubeUrl(e.target.value)}
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-semibold text-sm">Selected Files ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-muted rounded-lg p-3"
              >
                <div className="flex items-center gap-3">
                  <File className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeFile(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-vintage-yellow transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Upload Button */}
      <Button
        onClick={handleUpload}
        disabled={uploading || (files.length === 0 && !youtubeUrl)}
        className="w-full bg-vintage-yellow hover:bg-vintage-yellow/90 text-black font-medium"
        size="lg"
      >
        {uploading ? "Uploading..." : "Upload & Generate README"}
      </Button>
    </div>
  );
}
