"use client";

import { useState } from "react";
import { Folder, File, ChevronRight, ChevronDown } from "lucide-react";

interface FileTreeProps {
  tree: any;
}

interface TreeNodeProps {
  name: string;
  children?: any;
  level?: number;
}

function TreeNode({ name, children, level = 0 }: TreeNodeProps) {
  const [isOpen, setIsOpen] = useState(level < 2);
  const isFolder = children && Object.keys(children).length > 0;

  return (
    <div>
      <div
        className={`flex items-center gap-2 py-1 px-2 hover:bg-muted rounded cursor-pointer`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => setIsOpen(!isOpen)}
      >
        {isFolder && (
          <span>
            {isOpen ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </span>
        )}
        {isFolder ? (
          <Folder className="h-4 w-4 text-vintage-yellow" />
        ) : (
          <File className="h-4 w-4 text-muted-foreground" />
        )}
        <span className="text-sm">{name}</span>
      </div>

      {isFolder && isOpen && (
        <div>
          {Object.entries(children).map(([key, value]) => (
            <TreeNode key={key} name={key} children={value} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function FileTree({ tree }: FileTreeProps) {
  if (!tree) {
    return <p className="text-sm text-muted-foreground">No files</p>;
  }

  return (
    <div className="space-y-1">
      {Object.entries(tree).map(([key, value]) => (
        <TreeNode key={key} name={key} children={value} />
      ))}
    </div>
  );
}
