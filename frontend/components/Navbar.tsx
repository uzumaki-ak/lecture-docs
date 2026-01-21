"use client";

import Link from "next/link";
import { useTheme } from "next-themes";
import { Moon, Sun, User, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";

export function Navbar() {
  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-vintage-yellow flex items-center justify-center">
              <FileText className="h-5 w-5 text-black" />
            </div>
            <span className="font-bold text-xl">LectureDocs</span>
          </Link>

          {/* Right Side */}
          <div className="flex items-center gap-4">
            <ThemeToggle />
            
            <Button variant="ghost" size="sm">
              <User className="h-4 w-4 mr-2" />
              Account
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}