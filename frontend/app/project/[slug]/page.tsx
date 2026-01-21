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
  const { data: project, isLoading, refetch } = useQuery({
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
    const blob = new Blob([project?.readme_content || ""], { type: "text/markdown" });
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">{project?.name}</h1>
              <p className="text-muted-foreground mt-1">
                {project?.course_name} / {project?.module_name} / {project?.lecture_name}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRegenerate}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - README */}
          <div className="lg:col-span-2 space-y-4">
            {/* Toolbar */}
            <div className="flex items-center justify-between bg-card border border-border rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === "preview" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("preview")}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </Button>
                <Button
                  variant={viewMode === "raw" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("raw")}
                >
                  <Code className="h-4 w-4 mr-2" />
                  Raw
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={handleCopy}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
                <Button variant="ghost" size="sm" onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>

            {/* README Content */}
            <div className="bg-card border border-border rounded-lg p-8">
              <MarkdownViewer
                content={project?.readme_content || "# No README generated yet"}
                mode={viewMode}
              />
            </div>
          </div>

          {/* Right Column - Chat & Files */}
          <div className="space-y-6">
            {/* Chat Panel */}
            <div className="bg-card border border-border rounded-lg overflow-hidden">
              <div className="px-4 py-3 border-b border-border bg-muted/50">
                <h3 className="font-semibold">💬 Chat</h3>
              </div>
              <ChatPanel projectSlug={slug} />
            </div>

            {/* File Tree */}
            {project?.folder_tree && (
              <div className="bg-card border border-border rounded-lg overflow-hidden">
                <div className="px-4 py-3 border-b border-border bg-muted/50">
                  <h3 className="font-semibold">📁 Files</h3>
                </div>
                <div className="p-4">
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