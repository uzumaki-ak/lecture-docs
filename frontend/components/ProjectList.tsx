
"use client";

import { ProjectCard } from "./ProjectCard";

interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  course_name?: string;
  module_name?: string;
  lecture_name?: string;
  readme_content?: string;
  created_at: string;
  updated_at: string;
}

interface ProjectListProps {
  projects: Project[];
  isLoading: boolean;
  onRefetch: () => void;
}

export function ProjectList({ projects, isLoading, onRefetch }: ProjectListProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="h-64 bg-card border border-border rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-muted-foreground">
          No projects yet. Upload your first files to get started! 🚀
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">
          Your Projects ({projects.length})
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <ProjectCard key={project.id} project={project} onRefetch={onRefetch} />
        ))}
      </div>
    </div>
  );
}
