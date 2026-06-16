import { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const EXAMPLE_QUERIES = [
  "What are the best dark atmospheric RPGs?",
  "I liked Hollow Knight, what should I play next?",
  "Top rated co-op games with Metacritic above 85?",
  "Best strategy games on PC?",
  "Open world games with great storytelling?",
];

export default function App() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSearch = async (q) => {
    const question = q || query;
    if (!question.trim() || loading) return;

    setQuery("");
    setError(null);

    const userMessage = { role: "user", content: question };
    const newMessages = [...messages, { type: "user", text: question }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await axios.post(`${API_URL}/api/query`, {
        question,
        history,
      });

      const assistantMessage = { role: "assistant", content: res.data.answer };
      setHistory([...history, userMessage, assistantMessage]);
      setMessages([
        ...newMessages,
        { type: "assistant", text: res.data.answer, sources: res.data.sources },
      ]);
    } catch (err) {
      setError("Something went wrong. Please try again.");
      setMessages(newMessages.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  const clearChat = () => {
    setMessages([]);
    setHistory([]);
    setQuery("");
    setError(null);
  };

  const uniqueSources = (sources) =>
    sources.filter(
      (s, i, arr) =>
        arr.findIndex((x) => x.metadata.slug === s.metadata.slug) === i
    );

  const isEmpty = messages.length === 0;

  return (
    <div className="app">
      <header className={`header ${!isEmpty ? "header-compact" : ""}`}>
        <div className="logo">
          <span className="logo-icon">◈</span>
          <span className="logo-text">GameVaultAI</span>
        </div>
        {isEmpty && (
          <p className="tagline fade-in-delay">
            Ask anything about games. Get answers grounded in real reviews.
          </p>
        )}
        {!isEmpty && (
          <button className="clear-btn" onClick={clearChat}>
            New chat
          </button>
        )}
      </header>

      <main className="main">
        {isEmpty && (
          <div className="examples fade-in-delay-2">
            <p className="examples-label">Try asking</p>
            <div className="examples-grid">
              {EXAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  className="example-chip"
                  onClick={() => handleSearch(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {!isEmpty && (
          <div className="conversation">
            {messages.map((msg, i) => (
              <div key={i} className={`message message-${msg.type} fade-in`}>
                {msg.type === "user" ? (
                  <div className="user-bubble">{msg.text}</div>
                ) : (
                  <div className="assistant-bubble">
                    <span className="answer-label">Answer</span>
                    <p className="answer-text">{msg.text}</p>
                    {msg.sources?.length > 0 && (
                      <div className="sources">
                        <p className="sources-label">Sources</p>
                        <div className="sources-grid">
                          {uniqueSources(msg.sources).map((s) => (
                            <div key={s.metadata.slug} className="source-chip">
                              <span className="source-name">
                                {s.metadata.slug.replace(/-/g, " ")}
                              </span>
                              <div className="source-meta">
                                {s.metadata.metacritic > 0 && (
                                  <span className="meta-score">
                                    {s.metadata.metacritic} MC
                                  </span>
                                )}
                                {s.metadata.rating > 0 && (
                                  <span className="meta-rating">
                                    ★ {s.metadata.rating}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="message message-assistant fade-in">
                <div className="assistant-bubble">
                  <div className="loading-dots">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}

            {error && <div className="error-card fade-in">{error}</div>}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <div className={`input-bar ${!isEmpty ? "input-bar-stuck" : ""}`}>
        <div className={`search-wrapper ${loading ? "searching" : ""}`}>
          <input
            className="search-input"
            type="text"
            placeholder={isEmpty ? "Ask about games..." : "Ask a follow-up..."}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="search-btn"
            onClick={() => handleSearch()}
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <span className="spinner" />
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            )}
          </button>
        </div>
        <p className="input-hint">Powered by RAG · 364 games · GPT-4o-mini</p>
      </div>
    </div>
  );
}