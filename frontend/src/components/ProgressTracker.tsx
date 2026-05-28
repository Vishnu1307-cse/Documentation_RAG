import React from "react";
import { Loader2, CheckCircle2, Circle, AlertCircle } from "lucide-react";

interface ProgressTrackerProps {
  progressStep: string;
  status: string;
  errorMessage: string | null;
}

// Full chronological list of milestones to match backend logging
const PIPELINE_STEPS = [
  "Cloning repository...",
  "Parsing source files...",
  "Segmenting files into chunks...",
  "Generating semantic embeddings...",
  "Indexing chunks into vector database...",
  "Generating structured architectural documentation..."
];

export const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progressStep,
  status,
  errorMessage
}) => {
  // Utility to determine individual step completion states
  const getStepState = (stepText: string, index: number) => {
    if (status === "error") {
      // If we errored on this step, show error, otherwise show pending or complete
      if (progressStep === stepText) return "error";
      const activeIndex = PIPELINE_STEPS.indexOf(progressStep);
      return index < activeIndex ? "complete" : "pending";
    }
    
    if (status === "complete") return "complete";
    
    if (progressStep === stepText) return "active";
    
    const activeIndex = PIPELINE_STEPS.indexOf(progressStep);
    return index < activeIndex ? "complete" : "pending";
  };

  return (
    <div className="premium-card" style={{ maxWidth: "600px", margin: "0 auto" }}>
      <h3 style={{ fontSize: "1.5rem", marginBottom: "15px", color: "white", textAlign: "center" }}>
        Semantic ingestion in progress...
      </h3>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", textAlign: "center", marginBottom: "40px" }}>
        Please wait. Processing large repositories can take several minutes.
      </p>

      <div>
        {PIPELINE_STEPS.map((stepText, index) => {
          const stepState = getStepState(stepText, index);
          
          return (
            <div key={index} className="step-container">
              <div className={`step-icon ${stepState}`}>
                {stepState === "complete" && <CheckCircle2 size={18} />}
                {stepState === "active" && <Loader2 size={18} className="animate-spin" />}
                {stepState === "pending" && <Circle size={14} style={{ opacity: 0.3 }} />}
                {stepState === "error" && <AlertCircle size={18} />}
              </div>
              <div className={`step-text ${stepState === "active" ? "active" : ""}`}>
                {stepText}
              </div>
            </div>
          );
        })}
      </div>

      {status === "error" && errorMessage && (
        <div style={{
          background: "rgba(239, 68, 68, 0.08)",
          border: "1px solid rgba(239, 68, 68, 0.2)",
          borderRadius: "12px",
          padding: "20px",
          marginTop: "30px",
          color: "#f87171"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", fontWeight: 600, marginBottom: "8px" }}>
            <AlertCircle size={20} />
            Analysis Failed
          </div>
          <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>
            {errorMessage}
          </p>
        </div>
      )}
    </div>
  );
};
