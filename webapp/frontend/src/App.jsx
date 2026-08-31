import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import DragDropCanvas from "./components/DragDropCanvas";
import NodeGraphView from "./components/pipeline/NodeGraphView";
import NodeInspector from "./components/pipeline/NodeInspector";
import MTypeBaselineView from "./components/MTypeBaselineView";
import STypeDashboard from "./components/STypeDashboard";
import ComparisonView from "./components/ComparisonView";
import ExportView from "./components/ExportView";
import { UploadCloud, CheckCircle } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("pipeline");
  const [appState, setAppState] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [inspectingNode, setInspectingNode] = useState(null);

  const fetchState = async () => {
    try {
      setIsLoading(true);
      const res = await fetch("/api/state");
      if (!res.ok) throw new Error("Failed to load initial engine state.");
      const data = await res.json();
      setAppState(data);
      setErrorMessage(null);
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
  }, []);

  const handleUpload = async (configFile, datasetFile) => {
    try {
      setIsUploading(true);
      setErrorMessage(null);
      const formData = new FormData();
      if (configFile) formData.append("config_file", configFile);
      if (datasetFile) formData.append("dataset_file", datasetFile);

      const res = await fetch("/api/upload-files", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let detail = `Server error (${res.status})`;
        try {
          const errData = await res.json();
          detail = errData.detail || detail;
        } catch {
          const text = await res.text();
          if (text) detail = text;
        }
        throw new Error(detail);
      }
      const data = await res.json();
      setAppState(data);
      setActiveTab("pipeline");
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || "Failed to process uploaded files.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRunStype = async (params) => {
    try {
      setIsCalculating(true);
      setErrorMessage(null);
      const res = await fetch("/api/run-stype", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
      });

      if (!res.ok) {
        let detail = "S-Type calculation failed.";
        try {
          const errData = await res.json();
          detail = errData.detail || detail;
        } catch {}
        throw new Error(detail);
      }
      const data = await res.json();
      setAppState(data);
      setActiveTab("comparison");
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message || "Failed to run S-Type reduction.");
    } finally {
      setIsCalculating(false);
    }
  };

  const handleClearDataset = async () => {
    try {
      setIsLoading(true);
      const res = await fetch("/api/clear-dataset", { method: "POST" });
      if (!res.ok) throw new Error("Failed to clear dataset.");
      const data = await res.json();
      setAppState(data);
      setActiveTab("pipeline");
    } catch (err) {
      console.error(err);
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DragDropCanvas onUpload={handleUpload} isUploading={isUploading}>
      {/* Dark Navy Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        appState={appState}
        onClearDataset={handleClearDataset}
      />

      {/* Main Content Canvas */}
      <main className="flex-1 bg-white p-8 overflow-y-auto h-screen">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Error Alert Banner */}
          {errorMessage && (
            <div className="bg-red-50 border-2 border-red-600 text-red-900 px-4 py-3 rounded-md flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm">Upload/Processing Notice:</span>
                <span className="text-xs font-mono">{errorMessage}</span>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="text-xs font-bold text-red-700 hover:text-red-900 ml-4 px-2 py-1 bg-red-100 hover:bg-red-200 rounded border border-red-400"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Canvas Drag-and-Drop Prompt Bar */}
          <div className="app-card p-3.5 bg-slate-50 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-700">
              <UploadCloud className="w-4 h-4 text-[#ea580c]" />
              <span>
                <strong className="text-slate-900">Drag & Drop Active:</strong> Drag new <code className="bg-slate-200 px-1 py-0.5 rounded">.xlsx</code> or <code className="bg-slate-200 px-1 py-0.5 rounded">.csv</code> files anywhere onto the screen to reload data.
              </span>
            </div>
            <label className="btn-secondary px-3 py-1 cursor-pointer text-xs">
              Browse Files
              <input
                type="file"
                className="hidden"
                accept=".xlsx,.xls,.csv,.parquet,.txt"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  if (file.name.toLowerCase().endsWith(".xlsx") || file.name.toLowerCase().endsWith(".xls")) {
                    handleUpload(file, null);
                  } else {
                    handleUpload(null, file);
                  }
                  e.target.value = "";
                }}
              />
            </label>
          </div>

          {/* Active View Render */}
          {isLoading ? (
            <div className="app-card p-16 text-center">
              <div className="w-8 h-8 border-4 border-[#ea580c] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <h3 className="font-bold text-slate-900 text-lg">Initializing Orchestrated Pipeline...</h3>
              <p className="subtitle-teal text-xs mt-1">Registering modular skills and checking configuration</p>
            </div>
          ) : (
            <>
              {activeTab === "pipeline" && (
                <NodeGraphView
                  appState={appState}
                  onInspectNode={(node) => setInspectingNode(node)}
                />
              )}

              {activeTab === "mtype" && (
                <MTypeBaselineView
                  appState={appState}
                  onProceedToStype={() => setActiveTab("stype")}
                  onUploadBlockModel={(file) => handleUpload(null, file)}
                />
              )}

              {activeTab === "stype" && (
                <STypeDashboard
                  appState={appState}
                  onRunStype={handleRunStype}
                  isCalculating={isCalculating}
                />
              )}

              {activeTab === "comparison" && (
                <ComparisonView
                  appState={appState}
                  onProceedToExport={() => setActiveTab("export")}
                />
              )}

              {activeTab === "export" && (
                <ExportView appState={appState} />
              )}
            </>
          )}
        </div>
      </main>

      {/* Node Deep Inspection Drawer */}
      {inspectingNode && (
        <NodeInspector
          node={inspectingNode}
          onClose={() => setInspectingNode(null)}
        />
      )}
    </DragDropCanvas>
  );
}
