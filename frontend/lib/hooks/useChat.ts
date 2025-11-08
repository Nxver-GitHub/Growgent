/**
 * React Query hook for chat functionality.
 *
 * This hook will be connected to Agent 1's `/api/agents/chat` endpoint.
 *
 * @module hooks/useChat
 */

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { chatApi } from "../api";
import { useState, useCallback } from "react";

/**
 * Message interface for chat.
 */
export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  content: string;
  timestamp: string;
}

/**
 * Hook to manage chat messages and send messages to the agent.
 *
 * @returns Chat state and mutation functions
 */
export function useChat() {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  /**
   * Mutation to send a chat message.
   */
  const sendMessageMutation = useMutation({
    mutationFn: (message: string) => chatApi.sendMessage(message),
    onSuccess: (response, sentMessage) => {
      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        sender: "user",
        content: sentMessage,
        timestamp: new Date().toISOString(),
      };

      // Add bot response (structure depends on Agent 1's response format)
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        content: typeof response === "string" ? response : response.message || "Response received",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage, botMessage]);
    },
    onError: (error) => {
      console.error("Chat error:", error);
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        sender: "bot",
        content: "Sorry, I'm having trouble connecting. Please try again later.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    },
  });

  /**
   * Send a message to the agent.
   */
  const sendMessage = useCallback(
    (message: string) => {
      if (!message.trim()) return;
      sendMessageMutation.mutate(message);
    },
    [sendMessageMutation]
  );

  /**
   * Clear chat history.
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    sendMessage,
    clearMessages,
    isSending: sendMessageMutation.isPending,
    error: sendMessageMutation.error,
  };
}

