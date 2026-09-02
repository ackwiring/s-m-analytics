import React, { useState, useRef } from "react";
import { UploadCloud, FileSpreadsheet, Database, CheckCircle, AlertCircle } from "lucide-react";

export default function DragDropCanvas({ onUpload, isUploading, children }) {
  const [isDragging, setIsDragging] = useState(false);
  const dragCounter = useRef(0);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current++;
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current--;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragging(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    dragCounter.current = 0;
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files || []);
    if (!files.length) return;

    let configFile = null;
    let datasetFile = null;

    files.forEach(f => {
      const lower = f.name.toLowerCase();
      if (lower.endsWith('.xlsx') || lower.endsWith('.xls')) {
        configFile = f;
      } else {
        datasetFile = f;
      }
    });

    if (configFile || datasetFile) {
      await onUpload(configFile, datasetFile);
    }
  };

  return (
    <div 
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="relative min-h-screen w-full bg-white flex"
    >
      {/* Drag & Drop Visual Overlay with pointer-events-none */}
      {isDragging && (
        <div className="fixed inset-0 z-50 bg-[#0a192f]/90 flex flex-col items-center justify-center p-8 backdrop-blur-sm border-4 border-dashed border-[#f7901e] pointer-events-none select-none">
          <UploadCloud className="w-20 h-20 text-[#f7901e] animate-bounce mb-4" />
          <h2 className="text-3xl font-bold text-white mb-2">Drop Files to Ingest Data</h2>
          <p className="text-[#00a3a6] font-medium text-lg text-center max-w-md">
            Drop your <span className="text-white font-semibold">PhaseCalculator Config (.xlsx)</span> or <span className="text-white font-semibold">Block Model (.csv, .parquet)</span> anywhere.
          </p>
        </div>
      )}

      {/* Uploading Status Indicator */}
      {isUploading && (
        <div className="fixed bottom-6 right-6 z-40 bg-[#0a192f] border-2 border-black rounded-md px-6 py-3 text-white flex items-center gap-3">
          <div className="w-4 h-4 border-2 border-[#f7901e] border-t-transparent rounded-full animate-spin"></div>
          <span className="font-semibold text-sm">Processing uploaded dataset...</span>
        </div>
      )}

      {children}
    </div>
  );
}

