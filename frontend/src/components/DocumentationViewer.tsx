import React from "react";
import ReactMarkdown from "react-markdown";
import { Download, RefreshCw, FileText } from "lucide-react";

interface DocumentationViewerProps {
  markdown: string;
  onReset: () => void;
}

export const DocumentationViewer: React.FC<DocumentationViewerProps> = ({ markdown, onReset }) => {
  const handleDownload = () => {
    try {
      const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "codebase_technical_documentation.md");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error("Failed to download documentation file:", e);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "30px", maxWidth: "1000px", margin: "0 auto" }}>
      {/* Control Actions Header Bar */}
      <div className="premium-card" style={{ padding: "20px 30px", display: "flex", justifyContent: "between", alignItems: "center", flexWrap: "wrap", gap: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ background: "rgba(93, 95, 239, 0.15)", padding: "10px", borderRadius: "10px", color: "var(--border-focus)", display: "flex" }}>
            <FileText size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: "1.2rem", color: "white" }}>Technical Documentation</h3>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
              Semantic analysis completed successfully.
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "12px", marginLeft: "auto" }}>
          <button onClick={handleDownload} className="premium-btn btn-primary" style={{ padding: "12px 24px", fontSize: "0.925rem" }}>
            <Download size={16} />
            Download Markdown
          </button>
          
          <button onClick={onReset} className="premium-btn btn-secondary" style={{ padding: "12px 24px", fontSize: "0.925rem" }}>
            <RefreshCw size={16} />
            Analyze Another
          </button>
        </div>
      </div>

      {/* Main Documentation Viewer Surface */}
      <div className="premium-card markdown-body" style={{ padding: "50px" }}>
        {/* Renders secure react-markdown content with standard browser element fallbacks */}
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </div>
    </div>
  );
};
