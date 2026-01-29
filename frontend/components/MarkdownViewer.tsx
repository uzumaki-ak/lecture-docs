"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { useEffect } from "react";
import "highlight.js/styles/github-dark.css";

interface MarkdownViewerProps {
  content: string;
  mode?: "preview" | "raw";
}

export function MarkdownViewer({
  content,
  mode = "preview",
}: MarkdownViewerProps) {
  useEffect(() => {
    // Load highlight.js
    if (typeof window !== "undefined" && mode === "preview") {
      import("highlight.js").then((hljs) => {
        document.querySelectorAll("pre code").forEach((block) => {
          hljs.default.highlightElement(block as HTMLElement);
        });
      });
    }
  }, [content, mode]);

  if (mode === "raw") {
    return (
      <pre className="text-sm bg-muted p-4 rounded-lg overflow-x-auto whitespace-pre-wrap font-mono">
        <code>{content}</code>
      </pre>
    );
  }

  return (
    <div
      className="markdown-body prose prose-slate dark:prose-invert max-w-none w-full
                    prose-headings:font-bold prose-headings:tracking-tight
                    prose-h1:text-3xl sm:prose-h1:text-4xl prose-h1:mb-4 prose-h1:mt-8
                    prose-h2:text-2xl sm:prose-h2:text-3xl prose-h2:mb-3 prose-h2:mt-6
                    prose-h3:text-xl sm:prose-h3:text-2xl prose-h3:mb-2 prose-h3:mt-5
                    prose-p:text-sm sm:prose-p:text-base prose-p:leading-7 prose-p:my-4
                    prose-li:my-1 prose-ul:my-4 prose-ol:my-4
                    prose-strong:font-bold prose-strong:text-foreground
                    prose-code:text-xs sm:prose-code:text-sm prose-code:bg-gray-100 dark:prose-code:bg-gray-800
                    prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono
                    prose-code:before:content-none prose-code:after:content-none
                    prose-pre:bg-gray-900 prose-pre:text-gray-100 prose-pre:p-3 sm:prose-pre:p-4 prose-pre:rounded-lg
                    prose-pre:overflow-x-auto prose-pre:my-4 prose-pre:text-xs sm:prose-pre:text-sm
                    prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
                    prose-blockquote:border-l-4 prose-blockquote:border-gray-300 prose-blockquote:pl-4 prose-blockquote:italic
                    prose-blockquote:text-sm sm:prose-blockquote:text-base
                    prose-img:rounded-lg prose-img:shadow-md prose-img:max-w-full
                    prose-hr:my-8 prose-hr:border-gray-300 dark:prose-hr:border-gray-700
                    prose-table:border-collapse prose-table:w-full prose-table:text-xs sm:prose-table:text-sm
                    prose-th:border prose-th:border-gray-300 prose-th:p-2 prose-th:bg-gray-100
                    prose-td:border prose-td:border-gray-300 prose-td:p-2
                    overflow-hidden"
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            const isBlock = !!match;

            if (isBlock) {
              return (
                <div className="relative my-4 overflow-x-auto">
                  <div className="absolute top-2 right-2 text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded z-10">
                    {match[1]}
                  </div>
                  <pre className={`${className} overflow-x-auto`}>
                    <code {...props} className={className}>
                      {children}
                    </code>
                  </pre>
                </div>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          img({ node, src, alt, ...props }) {
            return (
              <img
                src={src}
                alt={alt}
                {...props}
                className="max-w-full h-auto rounded-lg shadow-md"
              />
            );
          },
          table({ node, children, ...props }) {
            return (
              <div className="overflow-x-auto my-4">
                <table {...props} className="border-collapse w-full text-sm">
                  {children}
                </table>
              </div>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
