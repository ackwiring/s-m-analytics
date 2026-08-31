import React from "react";
import { Download, FileArchive, CheckCircle2, ShieldAlert } from "lucide-react";
import InfoTooltip from "./InfoTooltip";

export default function ExportView({ appState }) {
  const handleDownload = () => {
    window.location.href = "/api/export-zip";
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold title-orange">Stage 4: Export Phase Files</h2>
        <p className="subtitle-teal text-sm">
          Download COMET-ready N-dimensional and 1-dimensional phase files and audit reports.
        </p>
      </div>

      <div className="app-card p-8 text-center space-y-6">
        <div className="w-16 h-16 bg-slate-200 border-2 border-black rounded-full flex items-center justify-center mx-auto text-[#ea580c]">
          <FileArchive className="w-8 h-8" />
        </div>

        <div className="max-w-md mx-auto space-y-2">
          <h3 className="text-xl font-bold text-slate-900">Compile & Bundle Deliverables</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Packages the standard M-Type files, all calculated S-Type percentile models, and verification audit sheets into a structured ZIP archive.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 max-w-lg mx-auto text-left text-xs font-mono bg-white p-4 rounded border border-slate-400">
          <div className="space-y-1 text-slate-700">
            <div>📁 MTYPE_PhaseFiles/</div>
            <div className="pl-4 text-slate-500">- Standard_PhaseFile_Data.csv</div>
            <div className="pl-4 text-slate-500">- MTYPE_df_mtypebins.csv</div>
          </div>
          <div className="space-y-1 text-slate-700">
            <div>📁 STYPE_*_PhaseFiles/</div>
            <div className="pl-4 text-slate-500">- STYPE_PhaseFile_Data.csv</div>
            <div className="pl-4 text-slate-500">- Audit_Report.txt</div>
          </div>
        </div>

        <InfoTooltip text="Downloads a single ZIP containing every phase file generated so far: the standard M-Type baseline, all calculated S-Type percentile runs, and their audit/verification reports.">
          <button
            onClick={handleDownload}
            className="btn-primary px-8 py-3 text-base flex items-center gap-3 mx-auto cursor-pointer"
          >
            <Download className="w-5 h-5" />
            <span>Download Files</span>
          </button>
        </InfoTooltip>
      </div>
    </div>
  );
}
