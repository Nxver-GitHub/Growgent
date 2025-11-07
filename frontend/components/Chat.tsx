/**
 * Chat component provides an interface for interacting with farm agents.
 *
 * Allows users to ask questions and receive recommendations from AI agents.
 *
 * @component
 * @returns {JSX.Element} The chat interface
 */
import { useState, useEffect, useRef, useCallback } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Send, Droplet, Trash2 } from "lucide-react";
import { ScrollArea } from "./ui/scroll-area";
import { Badge } from "./ui/badge";
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

export function Chat(): JSX.Element {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      sender: "bot",
      content: "Hello! How can I help your farm today?",
      timestamp: "10:00 AM",
    },
    {
      id: 2,
      sender: "user",
      content: "Should I irrigate today?",
      timestamp: "10:01 AM",
    },
    {
      id: 3,
      sender: "bot",
      content:
        "Based on current forecast and soil data, YES. I recommend: Irrigate Field 1 for 2 hours starting at 06:00 AM. Soil moisture 35%, drought risk high, fire risk low. This will save water vs. typical scheduling.",
      timestamp: "10:01 AM",
      actions: [
        { label: "View Schedule", onClick: () => console.log("View schedule") },
        { label: "Accept", onClick: () => console.log("Accept") },
      ],
    },
    {
      id: 4,
      sender: "user",
      content: "What about Field 3?",
      timestamp: "10:02 AM",
    },
    {
      id: 5,
      sender: "bot",
      content:
        "Field 3 crop health at 78% NDVI. Recommend fungicide spray Thursday. Current moisture levels are adequate, no immediate irrigation needed.",
      timestamp: "10:02 AM",
      actions: [
        { label: "View Heatmap", onClick: () => console.log("View heatmap") },
        { label: "Details", onClick: () => console.log("Details") },
      ],
    },
  ]);

  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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

  const quickActions = [
    { label: "/weather", action: "Show weather forecast" },
    { label: "/irrigation", action: "Check irrigation schedule" },
    { label: "/fire-risk", action: "View fire risk levels" },
    { label: "/help", action: "Get help" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2>Chat with Farm Agents</h2>
          <p className="text-slate-600">Ask questions and get intelligent recommendations</p>
        </div>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="outline" size="sm">
              <Trash2 className="h-4 w-4 mr-2" />
              Clear History
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Clear chat history?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete all messages in this conversation. This action cannot
                be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleClearHistory}>Clear</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Window */}
        <Card className="lg:col-span-3 p-6">
          <ScrollArea className="h-[500px] pr-4 mb-4" ref={scrollRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] ${
                      message.sender === "user"
                        ? "bg-emerald-600 text-white"
                        : "bg-slate-100 text-slate-900"
                    } rounded-lg p-4`}
                  >
                    <p className="mb-2">{message.content}</p>

                    {message.actions && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {message.actions.map((action, idx) => (
                          <Button
                            key={idx}
                            size="sm"
                            variant={message.sender === "user" ? "secondary" : "outline"}
                            onClick={action.onClick}
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
                  <div className="bg-slate-100 text-slate-900 rounded-lg p-4">
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
          <div className="flex gap-2">
            <Input
              placeholder="Type your question..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              className="flex-1"
            />
            <Button onClick={handleSend} className="bg-emerald-600 hover:bg-emerald-700">
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </Card>

        {/* Quick Actions Sidebar */}
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {quickActions.map((action, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => setInputValue(action.label)}
                >
                  <code className="mr-2 text-emerald-600">{action.label}</code>
                </Button>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h4 className="mb-3">Active Agents</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-slate-700">Fire-Adaptive Irrigation</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-slate-700">Water Efficiency</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span className="text-slate-700">PSPS Anticipation</span>
              </div>
            </div>
          </Card>

          <Card className="p-6 bg-emerald-50 border-emerald-200">
            <div className="flex items-start gap-3">
              <Droplet className="h-5 w-5 text-emerald-600 mt-1" />
              <div>
                <h4 className="text-emerald-900 mb-1">Tip</h4>
                <p className="text-emerald-700">
                  Try asking about specific fields, weather forecasts, or fire risk levels.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
