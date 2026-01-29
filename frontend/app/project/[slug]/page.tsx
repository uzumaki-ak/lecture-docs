"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { MarkdownViewer } from "@/components/MarkdownViewer";
import { ChatPanel } from "@/components/ChatPanel";
import { FileTree } from "@/components/FileTree";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { Download, RefreshCw, Copy, Eye, Code } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function ProjectPage() {
  const params = useParams();
  const slug = params?.slug as string;
  const [viewMode, setViewMode] = useState<"preview" | "raw">("preview");

  // Fetch project data
  const {
    data: project,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["project", slug],
    queryFn: () => api.get(`/projects/${slug}`),
    enabled: !!slug,
  });

  const handleRegenerate = async () => {
    try {
      await api.post(`/projects/${slug}/regenerate`);
      toast.success("README regeneration started!");
      setTimeout(() => refetch(), 5000);
    } catch (error) {
      toast.error("Failed to regenerate README");
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(project?.readme_content || "");
    toast.success("Copied to clipboard!");
  };

  const handleDownload = () => {
    const blob = new Blob([project?.readme_content || ""], {
      type: "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "README.md";
    a.click();
    toast.success("Downloaded README.md");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vintage-yellow"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b border-border bg-card sticky top-0 z-40">
        <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold truncate">
                {project?.name}
              </h1>
              <p className="text-xs sm:text-sm text-muted-foreground mt-1 truncate">
                {project?.course_name} / {project?.module_name}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRegenerate}
                className="text-xs sm:text-sm"
              >
                <RefreshCw className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                <span className="hidden sm:inline">Regenerate</span>
                <span className="sm:hidden">Regen</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-3 sm:px-4 py-4 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-8">
          {/* Left Column - README */}
          <div className="lg:col-span-2 space-y-4 min-w-0">
            {/* Toolbar */}
            <div className="flex flex-wrap items-center justify-between gap-2 bg-card border border-border rounded-lg p-2 sm:px-4 sm:py-3">
              <div className="flex items-center gap-1">
                <Button
                  variant={viewMode === "preview" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("preview")}
                  className="text-xs sm:text-sm"
                >
                  <Eye className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                  <span className="hidden sm:inline">Preview</span>
                </Button>
                <Button
                  variant={viewMode === "raw" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("raw")}
                  className="text-xs sm:text-sm"
                >
                  <Code className="h-3 w-3 sm:h-4 sm:w-4 mr-1" />
                  <span className="hidden sm:inline">Raw</span>
                </Button>
              </div>

              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className="text-xs sm:text-sm"
                >
                  <Copy className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span className="hidden sm:inline ml-1">Copy</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDownload}
                  className="text-xs sm:text-sm"
                >
                  <Download className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span className="hidden sm:inline ml-1">Download</span>
                </Button>
              </div>
            </div>

            {/* README Content */}
            <div className="bg-card border border-border rounded-lg p-3 sm:p-8 overflow-hidden">
              <MarkdownViewer
                content={project?.readme_content || "# No README generated yet"}
                mode={viewMode}
              />
            </div>
          </div>

          {/* Right Column - Chat & Files */}
          <div className="space-y-4 sm:space-y-6">
            {/* Chat Panel */}
            <div className="bg-card border border-border rounded-lg overflow-hidden">
              <div className="px-3 sm:px-4 py-2 sm:py-3 border-b border-border bg-muted/50">
                <h3 className="font-semibold text-sm sm:text-base">💬 Chat</h3>
              </div>
              <ChatPanel projectSlug={slug} />
            </div>

            {/* File Tree */}
            {project?.folder_tree && (
              <div className="bg-card border border-border rounded-lg overflow-hidden">
                <div className="px-3 sm:px-4 py-2 sm:py-3 border-b border-border bg-muted/50">
                  <h3 className="font-semibold text-sm sm:text-base">
                    📁 Files
                  </h3>
                </div>
                <div className="p-3 sm:p-4 overflow-y-auto max-h-96">
                  <FileTree tree={project.folder_tree} />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
