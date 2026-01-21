"use client";

import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { FileText, Trash2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface ProjectCardProps {
  project: any;
  onRefetch: () => void;
}

export function ProjectCard({ project, onRefetch }: ProjectCardProps) {
  const handleDelete = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (!confirm("Are you sure you want to delete this project?")) {
      return;
    }

    try {
      await api.delete(`/projects/${project.slug}`);
      toast.success("Project deleted");
      onRefetch();
    } catch (error) {
      toast.error("Failed to delete project");
    }
  };

  return (
    <Link href={`/project/${project.slug}`}>
      <div className="group bg-card border border-border rounded-lg p-6 hover:border-vintage-yellow transition-colors cursor-pointer h-full">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-lg group-hover:text-vintage-yellow transition-colors line-clamp-1">
              {project.name}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              {project.course_name && `${project.course_name} / `}
              {project.module_name && `${project.module_name} / `}
              {project.lecture_name}
            </p>
          </div>
          
          <div className="flex items-center gap-1">
            {project.readme_content && (
              <div className="h-2 w-2 rounded-full bg-green-500" title="README generated" />
            )}
          </div>
        </div>

        {/* Description */}
        {project.description && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {project.description}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-border">
          <span className="text-xs text-muted-foreground">
            {formatDistanceToNow(new Date(project.created_at), { addSuffix: true })}
          </span>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        </div>
      </div>
    </Link>
  );
}
