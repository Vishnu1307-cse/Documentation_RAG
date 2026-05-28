import { useState, useEffect, useRef } from "react";
import { UrlInput } from "./components/UrlInput";
import { ProgressTracker } from "./components/ProgressTracker";
import { DocumentationViewer } from "./components/DocumentationViewer";
import { GitPullRequest, Shield } from "lucide-react";

type ViewState = "input" | "progress" | "result";

function App() {
  const [view, setView] = useState<ViewState>("input");
  
  // Job trackers
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("pending");
  const [progressStep, setProgressStep] = useState<string>("Job enqueued...");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [markdown, setMarkdown] = useState<string>("");

  const pollIntervalRef = useRef<number | null>(null);
  const backendBaseUrl = "http://127.0.0.1:8000";

  const handleStartAnalysis = async (url: string, provider: string) => {
    setView("progress");
    setStatus("pending");
    setProgressStep("Submitting analysis job...");
    setErrorMessage(null);

    try {
      const response = await fetch(`${backendBaseUrl}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: url, llm_provider: provider })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to start repository analysis.");
      }

      const data = await response.json();
      setJobId(data.job_id);
    } catch (e: any) {
      setStatus("error");
      setErrorMessage(e.message || "An unexpected network error occurred.");
    }
  };

  // Status Polling Effect
  useEffect(() => {
    if (!jobId || view !== "progress") return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`${backendBaseUrl}/api/jobs/${jobId}/status`);
        if (!response.ok) {
          throw new Error("Failed to poll background task status.");
        }

        const data = await response.json();
        setStatus(data.status);
        setProgressStep(data.progress_step);

        if (data.status === "complete") {
          clearInterval(pollIntervalRef.current!);
          // Fetch final markdown
          fetchResult();
        } else if (data.status === "error") {
          clearInterval(pollIntervalRef.current!);
          setErrorMessage(data.error_message || "An execution error occurred inside the ingestion pipeline.");
        }
      } catch (e: any) {
        clearInterval(pollIntervalRef.current!);
        setStatus("error");
        setErrorMessage(e.message || "A connection loss was encountered while polling.");
      }
    };

    pollIntervalRef.current = window.setInterval(pollStatus, 2000);

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [jobId, view]);

  const fetchResult = async () => {
    if (!jobId) return;

    try {
      const response = await fetch(`${backendBaseUrl}/api/jobs/${jobId}/result`);
      if (!response.ok) {
        throw new Error("Failed to load completed documentation content.");
      }

      const mdText = await response.text();
      setMarkdown(mdText);
      setView("result");
    } catch (e: any) {
      setStatus("error");
      setErrorMessage(e.message || "An error occurred fetching the final results.");
    }
  };

  const handleReset = () => {
    setView("input");
    setJobId(null);
    setStatus("pending");
    setProgressStep("Job enqueued...");
    setErrorMessage(null);
    setMarkdown("");
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Premium Header/Banner Branding */}
      <header style={{
        padding: "30px 5%",
        display: "flex",
        justifyContent: "between",
        alignItems: "center",
        borderBottom: "1px solid var(--border-color)",
        backgroundColor: "rgba(11, 13, 19, 0.4)",
        backdropFilter: "blur(10px)",
        position: "sticky",
        top: 0,
        zIndex: 50
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }} onClick={handleReset}>
          <div style={{
            background: "var(--grad-primary)",
            borderRadius: "10px",
            padding: "8px",
            display: "flex",
            color: "white"
          }}>
            <GitPullRequest size={20} />
          </div>
          <span style={{ fontFamily: "var(--font-family-title)", fontWeight: 800, fontSize: "1.25rem", letterSpacing: "-0.03em" }}>
            GitDoc<span style={{ color: "var(--border-focus)" }}>.rag</span>
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-muted)", fontSize: "0.85rem", marginLeft: "auto" }}>
          <Shield size={14} />
          Secure Client Session
        </div>
      </header>

      {/* Primary Main Content View Routing */}
      <main style={{ flex: 1, padding: "80px 5%", display: "flex", flexDirection: "column", justifyContent: "center" }}>
        {view === "input" && (
          <div style={{ maxWidth: "650px", margin: "0 auto", width: "100%" }}>
            <UrlInput onSubmit={handleStartAnalysis} isLoading={status === "processing"} />
          </div>
        )}

        {view === "progress" && (
          <ProgressTracker
            progressStep={progressStep}
            status={status}
            errorMessage={errorMessage}
          />
        )}

        {view === "result" && (
          <DocumentationViewer markdown={markdown} onReset={handleReset} />
        )}
      </main>

      {/* Sleek Minimal Footer */}
      <footer style={{
        padding: "30px",
        textAlign: "center",
        borderTop: "1px solid var(--border-color)",
        color: "var(--text-muted)",
        fontSize: "0.85rem"
      }}>
        GitDoc.rag Codebase Documentation System &copy; 2026. Made with Google Generative AI capabilities.
      </footer>
    </div>
  );
}

export default App;
