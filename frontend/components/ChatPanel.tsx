"use client";

import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface ChatPanelProps {
  projectSlug: string;
}

export function ChatPanel({ projectSlug }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // Fetch chat history
  const { data: chatHistory } = useQuery({
    queryKey: ["chat", projectSlug],
    queryFn: () => api.get(`/projects/${projectSlug}/chat/history`),
    refetchInterval: 5000, // Poll every 5 seconds
  });

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: (msg: string) =>
      api.post(`/projects/${projectSlug}/chat`, { message: msg }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat", projectSlug] });
      setMessage("");
    },
    onError: () => {
      toast.error("Failed to send message");
    },
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    sendMutation.mutate(message);
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  return (
    <div className="flex flex-col h-[600px]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatHistory?.messages?.length === 0 ? (
          <div className="text-center text-sm text-muted-foreground py-8">
            <Bot className="h-12 w-12 mx-auto mb-2 text-vintage-yellow" />
            <p>Ask me anything about this project!</p>
          </div>
        ) : (
          chatHistory?.messages?.map((msg: any, index: number) => (
            <div
              key={index}
              className={`flex gap-3 ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {msg.role === "assistant" && (
                <div className="h-8 w-8 rounded-full bg-vintage-yellow flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4 text-black" />
                </div>
              )}
              
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.role === "user"
                    ? "bg-vintage-yellow text-black"
                    : "bg-muted"
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.retrieved_chunks && msg.retrieved_chunks.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/50">
                    <p className="text-xs text-muted-foreground">
                      📚 {msg.retrieved_chunks.length} source{msg.retrieved_chunks.length > 1 ? 's' : ''}
                    </p>
                  </div>
                )}
              </div>

              {msg.role === "user" && (
                <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask a question..."
            disabled={sendMutation.isPending}
          />
          <Button
            type="submit"
            disabled={!message.trim() || sendMutation.isPending}
            className="bg-vintage-yellow hover:bg-vintage-yellow/90 text-black"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}