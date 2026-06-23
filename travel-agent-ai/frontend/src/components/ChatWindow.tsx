import React, { useState, useRef, useEffect } from "react";
import { Input, Button, Spin } from "antd";
import { SendOutlined } from "@ant-design/icons";
import { sendMessage } from "../api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Plan a 5-day trip to Bali in October",
  "Weather in Lisbon next month?",
  "Budget for 7 days in Japan, mid-range",
  "Best time to visit Iceland",
];

function getGreeting(): { eyebrow: string; line: string } {
  const hour = new Date().getHours();
  if (hour < 5) return { eyebrow: "Still up?", line: "Where shall we send you next?" };
  if (hour < 12) return { eyebrow: "Good morning", line: "Where to today?" };
  if (hour < 17) return { eyebrow: "Good afternoon", line: "Let's plan your next escape." };
  if (hour < 21) return { eyebrow: "Good evening", line: "Dreaming of somewhere new?" };
  return { eyebrow: "Good night", line: "A little wanderlust before bed?" };
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const greeting = getGreeting();

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const submit = async (text: string) => {
    if (!text.trim()) return;
    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendMessage(text, sessionId);
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't reach the agent. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="stars" />
      <div className="horizon-glow" />

      <div className="boarding-header">
        <div className="mark">✈</div>
        <div>
          <p className="title">Wanderly</p>
          <p className="subtitle">AI Travel Agent · Boarding Pass to Anywhere</p>
        </div>
      </div>

      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="greeting-hero">
            <div className="eyebrow">{greeting.eyebrow}</div>
            <h1>{greeting.line}</h1>
            <p>Tell me a destination, your dates, and a rough budget — I'll handle weather, costs, and a day-by-day plan.</p>
            <div style={{ marginTop: 20 }}>
              {SUGGESTIONS.map((s) => (
                <span key={s} className="suggestion-chip" onClick={() => submit(s)}>
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`bubble-row ${msg.role}`}>
            <div style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
              {msg.role === "assistant" && <div className="avatar-mark assistant">🧭</div>}
              <div className={`bubble ${msg.role}`}>{msg.content}</div>
              {msg.role === "user" && <div className="avatar-mark user">🙂</div>}
            </div>
          </div>
        ))}

        {loading && (
          <div className="bubble-row assistant">
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <div className="avatar-mark assistant">🧭</div>
              <div className="bubble assistant">
                <Spin size="small" /> <span style={{ marginLeft: 8 }}>Charting your route...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="composer-bar">
        <div style={{ display: "flex", gap: 8 }}>
          <Input.TextArea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. Plan a 5-day mid-range trip to Bali in October"
            autoSize={{ minRows: 1, maxRows: 4 }}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                submit(input);
              }
            }}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={() => submit(input)} loading={loading}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
