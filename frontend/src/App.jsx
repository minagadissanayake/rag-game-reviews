import { useState } from "react";
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
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (q) => {
    const question = q || query;
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setAnswer(null);
    setSources([]);
    setQuery(question);

    try {
      const res = await axios.post(`${API_URL}/api/query`, { question });
      setAnswer(res.data.answer);
      setSources(res.data.sources);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  const uniqueSources = sources.filter(
    (s, i, arr) => arr.findIndex((x) => x.metadata.slug === s.metadata.slug) === i
  );

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">◈</span>
          <span className="logo-text">GameVaultAI</span>
        </div>
        <p className="tagline">Ask anything about games. Get answers grounded in real reviews.</p>
      </header>

      <main className="main">
        <div className={`search-wrapper ${loading ? "searching" : ""}`}>
          <input
            className="search-input"
            type="text"
            placeholder="Ask about games..."
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

        {!answer && !loading && (
          <div className="examples">
            <p className="examples-label">Try asking</p>
            <div className="examples-grid">
              {EXAMPLE_QUERIES.map((q) => (
                <button key={q} className="example-chip" onClick={() => handleSearch(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-state">
            <div className="loading-bar" />
            <p className="loading-text">Searching through 364 games...</p>
          </div>
        )}

        {error && <div className="error-card">{error}</div>}

        {answer && (
          <div className="answer-card">
            <div className="answer-header">
              <span className="answer-label">Answer</span>
            </div>
            <p className="answer-text">{answer}</p>

            {uniqueSources.length > 0 && (
              <div className="sources">
                <p className="sources-label">Sources</p>
                <div className="sources-grid">
                  {uniqueSources.map((s) => (
                    <div key={s.metadata.slug} className="source-chip">
                      <span className="source-name">
                        {s.metadata.slug.replace(/-/g, " ")}
                      </span>
                      <div className="source-meta">
                        {s.metadata.metacritic > 0 && (
                          <span className="meta-score">{s.metadata.metacritic} MC</span>
                        )}
                        {s.metadata.rating > 0 && (
                          <span className="meta-rating">★ {s.metadata.rating}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Powered by RAG · 364 games indexed · GPT-4o-mini</p>
      </footer>
    </div>
  );
}