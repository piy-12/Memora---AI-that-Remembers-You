import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const USER_ID = "user_123";

function App() {
  const [activePage, setActivePage] = useState("chat");

  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState([]);

  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);

  // Load conversation history from FastAPI
  const fetchHistory = async () => {
    setIsLoadingHistory(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/history/${USER_ID}`);

      if (!response.ok) {
        throw new Error("Failed to load conversation history.");
      }

      const data = await response.json();
      setHistory(data.messages || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Fetch history whenever the History page is opened
  useEffect(() => {
    if (activePage === "history") {
      fetchHistory();
    }
  }, [activePage]);

  // Automatically scroll to the latest chat message
  useEffect(() => {
    if (activePage === "chat") {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [messages, isSending, activePage]);

  // Send a message to Memora
  const handleSendMessage = async () => {
    const message = input.trim();

    if (!message || isSending) return;

    setInput("");
    setError("");

    // Display the user's message immediately
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      },
    ]);

    setIsSending(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: USER_ID,
          message,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to get a response from Memora.");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSending(false);
    }
  };

  // Handle Enter key
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  // Format message timestamps
  const formatDate = (timestamp) => {
    if (!timestamp) return "Date unavailable";

    return new Date(timestamp).toLocaleString([], {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  // Chat interface
  const renderChat = () => (
    <>
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <div className="welcome-icon">✧</div>
            <h1>Welcome to Memora.</h1>
            <p>
              A space to think, reflect, and talk.
              <br />
              I'm here whenever you need me.
            </p>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message, index) => (
              <div key={index} className={`message-row ${message.role}`}>
                {message.role === "assistant" && (
                  <div className="message-avatar">M</div>
                )}
                <div className="message-content">
                  <div className="message-role">
                    {message.role === "user" ? "You" : "Memora"}
                  </div>
                  <div className="message-text">{message.content}</div>
                </div>
              </div>
            ))}

            {isSending && (
              <div className="message-row assistant">
                <div className="message-avatar">M</div>
                <div className="message-content">
                  <div className="message-role">Memora</div>
                  <div className="typing-indicator">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="input-section">
        <div className="input-wrapper">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Share what's on your mind..."
            rows={1}
            disabled={isSending}
          />
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!input.trim() || isSending}
          >
            ↑
          </button>
        </div>
        <p className="input-hint">
          Press Enter to send · Shift + Enter for a new line
        </p>
      </div>
    </>
  );

  // History interface
  const renderHistory = () => (
    <div className="history-container">
      {isLoadingHistory ? (
        <p className="history-empty">Loading history...</p>
      ) : history.length === 0 ? (
        <p className="history-empty">No conversation history yet.</p>
      ) : (
        history.map((message, index) => (
          <div className="history-card" key={index}>
            <div className="history-card-header">
              <span className="history-role">
                {message.role === "user" ? "You" : "Memora"}
              </span>
              <span className="history-date">
                {formatDate(message.created_at)}
              </span>
            </div>
            <div className="history-content">{message.content}</div>
          </div>
        ))
      )}
    </div>
  );

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">M</div>
          <span>memora</span>
        </div>

        <div className="sidebar-content">
          <p className="sidebar-label">WORKSPACE</p>

          <button
            className={`sidebar-item ${activePage === "chat" ? "active" : ""}`}
            onClick={() => {
              setActivePage("chat");
              setError("");
            }}
          >
            <span>✧</span>
            Chat
          </button>

          <button
            className={`sidebar-item ${activePage === "history" ? "active" : ""}`}
            onClick={() => {
              setActivePage("history");
              setError("");
            }}
          >
            <span>◷</span>
            History
          </button>
        </div>

        <div className="sidebar-footer">
          <div className="profile-avatar">P</div>
          <div>
            <p className="profile-name">Piyush</p>
            <p className="profile-subtitle">Personal space</p>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="chat-container">
        <header className="chat-header">
          <div>
            <h2>
              {activePage === "chat" ? "Memora" : "Conversation History"}
            </h2>
            <p>
              {activePage === "chat"
                ? "Your personal AI companion"
                : "Your conversations over time"}
            </p>
          </div>
        </header>

        {error && <div className="error-message">{error}</div>}

        {activePage === "chat" && renderChat()}
        {activePage === "history" && renderHistory()}
      </main>
    </div>
  );
}

export default App;