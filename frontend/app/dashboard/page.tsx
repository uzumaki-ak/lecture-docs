"use client";

import { useState, useEffect } from "react"; // ADD useEffect
import { useQuery } from "@tanstack/react-query";
import { ProjectList } from "@/components/ProjectList";
import { UploadZone } from "@/components/UploadZone";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Filter, FolderPlus } from "lucide-react";
import { toast } from "sonner";

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [showUpload, setShowUpload] = useState(false);
  const [filters, setFilters] = useState({
    course: "",
    module: "",
  });
  const [isClient, setIsClient] = useState(false); // ADD this

  // ADD this useEffect
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Fetch projects
  const {
    data: projectsData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["projects", searchQuery, filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append("search", searchQuery);
      if (filters.course) params.append("course", filters.course);
      if (filters.module) params.append("module", filters.module);

      try {
        const response = await api.get(`/projects?${params.toString()}`);
        // Ensure response has the expected structure
        if (response && (response.projects || response.total !== undefined)) {
          return response;
        }
        // Return default structure if response is malformed
        return { projects: [], total: 0, page: 1, page_size: 20 };
      } catch (error) {
        console.error("Failed to fetch projects:", error);
        return { projects: [], total: 0, page: 1, page_size: 20 };
      }
    },
    enabled: isClient, // ADD this - only run queries on client
  });

  // Fetch available filters
  const { data: filtersData } = useQuery({
    queryKey: ["filters"],
    queryFn: async () => {
      try {
        const response = await api.get("/filters");
        // Check if response is valid
        if (response && (response.courses || response.modules)) {
          return response;
        }
        // Return empty structure if invalid
        return { courses: [], modules: [] };
      } catch (error) {
        console.error("Failed to fetch filters:", error);
        return { courses: [], modules: [] };
      }
    },
    enabled: isClient, // ADD this
  });

  const handleUploadComplete = () => {
    setShowUpload(false);
    refetch();
    toast.success("Files uploaded successfully! Processing started.");
  };

  // ADD conditional rendering at the beginning
  if (!isClient) {
    return <div>Loading...</div>;
  }
  console.log("DEBUG - projectsData:", projectsData);
console.log("DEBUG - filtersData:", filtersData);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">
            Welcome back! 👋
          </h1>
          <p className="text-muted-foreground mt-2">
            Transform your learning materials into structured documentation
          </p>
        </div>

        <Button
          onClick={() => setShowUpload(!showUpload)}
          size="lg"
          className="bg-vintage-yellow hover:bg-vintage-yellow/90 text-black font-medium"
        >
          <FolderPlus className="mr-2 h-5 w-5" />
          New Project
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Projects</p>
              <p className="text-3xl font-bold mt-1">
                {projectsData?.total || 0}
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-vintage-yellow/20 flex items-center justify-center">
              <FolderPlus className="h-6 w-6 text-vintage-yellow" />
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">READMEs Generated</p>
              <p className="text-3xl font-bold mt-1">
                {projectsData?.projects?.filter((p: any) => p.readme_content)
                  .length || 0}
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-green-500/20 flex items-center justify-center">
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Recent Activity</p>
              <p className="text-3xl font-bold mt-1">3</p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <span className="text-2xl">⚡</span>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Ready to Create</p>
              <p className="text-3xl font-bold mt-1">
                <span className="text-vintage-yellow">New</span>
              </p>
            </div>
            <div className="h-12 w-12 rounded-lg bg-vintage-yellow/20 flex items-center justify-center">
              <span className="text-2xl">🚀</span>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      {showUpload && (
        <div className="bg-card border-2 border-dashed border-vintage-yellow rounded-lg p-8">
          <UploadZone onComplete={handleUploadComplete} />
        </div>
      )}

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <select
          value={filters.course}
          onChange={(e) => setFilters({ ...filters, course: e.target.value })}
          className="px-4 py-2 border border-border rounded-lg bg-background"
        >
          <option value="">All Courses</option>
          {filtersData?.courses?.map((course: string) => (
            <option key={course} value={course}>
              {course}
            </option>
          ))}
        </select>

        <select
          value={filters.module}
          onChange={(e) => setFilters({ ...filters, module: e.target.value })}
          className="px-4 py-2 border border-border rounded-lg bg-background"
        >
          <option value="">All Modules</option>
          {filtersData?.modules?.map((module: string) => (
            <option key={module} value={module}>
              {module}
            </option>
          ))}
        </select>
      </div>

      {/* Projects List */}
      <ProjectList
        projects={projectsData?.projects || []}
        isLoading={isLoading}
        onRefetch={refetch}
      />
    </div>
  );
}
