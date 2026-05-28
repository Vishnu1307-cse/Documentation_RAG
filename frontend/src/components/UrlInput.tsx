import React, { useState } from "react";
import { GitBranch, AlertCircle, ArrowRight } from "lucide-react";

interface UrlInputProps {
  onSubmit: (url: string, provider: string) => void;
  isLoading: boolean;
}

export const UrlInput: React.FC<UrlInputProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState("");
  const [provider, setProvider] = useState("openai");
  const [error, setError] = useState<string | null>(null);

  // Strict regex to check URL format client-side before dispatching
  const GITHUB_URL_REGEX = /^https:\/\/github\.com\/[a-zA-Z0-9_\-\.]+\/[a-zA-Z0-9_\-\.]+\/?$/;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const formattedUrl = url.trim();

    if (!formattedUrl) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    if (!GITHUB_URL_REGEX.test(formattedUrl)) {
      setError("Invalid GitHub format. Example: https://github.com/owner/repo");
      return;
    }

    onSubmit(formattedUrl, provider);
  };

  return (
    <div className="premium-card">
      <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "30px" }}>
        <div style={{ background: "var(--grad-primary)", padding: "12px", borderRadius: "14px", display: "flex" }}>
          <GitBranch size={28} color="white" />
        </div>
        <div>
          <h2 style={{ fontSize: "1.75rem", color: "white" }}>Semantic Codebase Analyzer</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Generate comprehensive structural architectural docs instantly using RAG
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="repo-url">GitHub Repository URL</label>
          <input
            id="repo-url"
            type="text"
            className="premium-input"
            placeholder="https://github.com/tiangolo/fastapi"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            autoComplete="off"
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="llm-provider">Active LLM Provider</label>
          <select
            id="llm-provider"
            className="premium-select"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            disabled={isLoading}
          >
            <option value="openai">OpenAI (gpt-4o-mini)</option>
            <option value="anthropic">Claude (claude-3-5-haiku)</option>
            <option value="gemini">Google Gemini (gemini-1.5-flash)</option>
            <option value="deepseek">DeepSeek (deepseek-chat)</option>
          </select>
        </div>

        {error && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.2)",
            borderRadius: "10px",
            padding: "12px 16px",
            marginBottom: "24px",
            color: "#f87171"
          }}>
            <AlertCircle size={20} />
            <span style={{ fontSize: "0.925rem" }}>{error}</span>
          </div>
        )}

        <button
          type="submit"
          className="premium-btn btn-primary"
          style={{ width: "100%" }}
          disabled={isLoading}
        >
          {isLoading ? "Processing Request..." : "Analyze Repository"}
          {!isLoading && <ArrowRight size={18} />}
        </button>
      </form>
    </div>
  );
};
