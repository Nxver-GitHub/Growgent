/**
 * ChatBubble component provides a collapsible chat interface on the right side of the screen.
 *
 * Displays as a collapsible panel similar to ChatGPT/Claude, integrated into the layout.
 *
 * @component
 * @returns {JSX.Element} The collapsible chat panel interface
 */
import { useState, useEffect, useRef } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Send, MessageSquare, Trash2, X } from "lucide-react";
import { ScrollArea } from "./ui/scroll-area";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "./ui/alert-dialog";
import { toast } from "sonner";

interface Message {
  /** Unique message identifier */
  id: number;
  /** Sender of the message */
  sender: "user" | "bot";
  /** Message content */
  content: string;
  /** Timestamp of the message */
  timestamp: string;
  /** Optional action buttons for the message */
  actions?: { label: string; onClick: () => void }[];
}

interface ChatBubbleProps {
  /** Whether the chat panel is open */
  isOpen: boolean;
  /** Callback to toggle the chat panel */
  onToggle: () => void;
}

export function ChatBubble({ isOpen, onToggle }: ChatBubbleProps): JSX.Element {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "bot",
      content: "Hello! How can I help your farm today?",
      timestamp: "10:00 AM",
    },
  ]);

  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current && isOpen) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  const handleSend = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: messages.length + 1,
      sender: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages([...messages, newMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botMessage: Message = {
        id: messages.length + 2,
        sender: "bot",
        content:
          "I'm analyzing your request. This is a demo response showing how the chat interface works.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000);
  };

  const handleClearHistory = () => {
    setMessages([
      {
        id: 1,
        sender: "bot",
        content: "Hello! How can I help your farm today?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    toast.success("Chat history cleared");
  };

  return (
    <>
      {/* Collapsed Square Button - Bottom right corner, safe from scrollbars */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed bottom-6 right-6 z-[100] bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-lg w-14 h-14 flex items-center justify-center transition-all duration-200 hover:scale-110 group"
          aria-label="Open chat"
          data-chat-bubble="button"
        >
          <MessageSquare className="h-6 w-6 group-hover:scale-110 transition-transform" />
        </button>
      )}

      {/* Expanded Chat Window - Floating window bottom right, safe from scrollbars */}
      {isOpen && (
        <div 
          className="fixed bottom-6 right-6 w-96 h-[600px] bg-white border border-slate-200 rounded-lg shadow-2xl flex flex-col z-[100] transition-all duration-300 ease-in-out"
          data-chat-bubble="window"
        >
          {/* Header */}
          <div className="h-16 bg-emerald-600 text-white px-4 flex items-center justify-between flex-shrink-0 rounded-t-lg">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              <span className="font-semibold">Chat with Agents</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-white hover:bg-emerald-700"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Clear chat history?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will permanently delete all messages in this conversation. This action
                      cannot be undone.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleClearHistory}>Clear</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white hover:bg-emerald-700"
                onClick={onToggle}
                aria-label="Close chat"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Chat Content */}
          <ScrollArea className="flex-1 px-4 py-4" ref={scrollRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] ${
                      message.sender === "user"
                        ? "bg-emerald-600 text-white"
                        : "bg-slate-100 text-slate-900"
                    } rounded-lg p-3`}
                  >
                    <p className="text-sm mb-1">{message.content}</p>

                    {message.actions && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {message.actions.map((action, idx) => (
                          <Button
                            key={idx}
                            size="sm"
                            variant={message.sender === "user" ? "secondary" : "outline"}
                            onClick={action.onClick}
                            className="h-7 text-xs"
                          >
                            {action.label}
                          </Button>
                        ))}
                      </div>
                    )}

                    <p
                      className={`text-xs mt-2 ${
                        message.sender === "user" ? "text-emerald-100" : "text-slate-500"
                      }`}
                    >
                      {message.timestamp}
                    </p>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-slate-100 text-slate-900 rounded-lg p-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                      <div
                        className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                      <div
                        className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.4s" }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Input Area */}
          <div className="h-16 border-t border-slate-200 px-4 flex items-center gap-2 flex-shrink-0 rounded-b-lg">
            <Input
              placeholder="Type your question..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              className="flex-1 h-10"
            />
            <Button
              onClick={handleSend}
              className="bg-emerald-600 hover:bg-emerald-700 h-10 w-10 p-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </>
  );
}

