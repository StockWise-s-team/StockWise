"use client";

import { useSSE } from "@/hooks/useSSE";
import { AgentThoughtStream } from "@/components/advisor/AgentThoughtStream";
import { useState } from "react";

export default function AdvisorPage() {
  const [message, setMessage] = useState("");
  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);
  const events = useSSE(
    submittedMessage
      ? `/advisor/chat/stream?message=${encodeURIComponent(submittedMessage)}`
      : null
  );

  const handleSend = () => {
    if (!message.trim()) return;
    setSubmittedMessage(message.trim());
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <h1 className="mb-4 text-3xl font-bold">AI Advisor</h1>
      <div className="flex flex-1 flex-col rounded-lg border bg-card shadow-sm">
        <div className="flex-1 overflow-auto p-4">
          {events.map((event, i) => (
            <AgentThoughtStream key={i} event={event} />
          ))}
          {!submittedMessage && (
            <div className="flex h-full items-center justify-center text-muted-foreground">
              <p>Ask the AI advisor anything about stocks, markets, or your portfolio.</p>
            </div>
          )}
        </div>
        <div className="border-t p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              className="flex-1 rounded-md border px-3 py-2 text-sm"
              placeholder="Ask a question..."
            />
            <button
              onClick={handleSend}
              className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
