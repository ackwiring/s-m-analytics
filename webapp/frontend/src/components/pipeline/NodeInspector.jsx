import React from "react";
import { X, Clock, Terminal, CheckCircle2, AlertCircle } from "lucide-react";
import InfoTooltip from "../InfoTooltip";

export default function NodeInspector({ node, onClose }) {
  if (!node) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end">
      <div className="w-[480px] bg-[#0a192f] text-slate-200 h-full border-l-2 border-black p-6 flex flex-col justify-between shadow-2xl animate-in slide-in-from-right">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#00a3a6]">{node.category} Skill</span>
              <h3 className="text-lg font-bold text-white">{node.display_name}</h3>
            </div>
            <InfoTooltip text="Closes this inspector panel. Does not stop or re-run the skill." position="left">
              <button
                onClick={onClose}
                className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </InfoTooltip>
          </div>

          {/* Node Meta */}
          <div className="space-y-4">
            <div className="bg-slate-900/90 p-3 rounded border border-slate-700 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Skill Identifier:</span>
                <span className="font-mono text-slate-200">{node.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Version:</span>
                <span className="font-mono text-slate-200">{node.version}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Execution Status:</span>
                <span className={`font-bold uppercase ${node.status === "COMPLETED" ? "text-emerald-400" : "text-amber-400"}`}>
                  {node.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Execution Time:</span>
                <span className="font-mono text-slate-200">{node.timing_ms} ms</span>
              </div>
            </div>

            {/* Description */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Description</h4>
              <p className="text-xs text-slate-300 bg-slate-900/60 p-2.5 rounded border border-slate-800">
                {node.description}
              </p>
            </div>

            {/* Console Logs */}
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-[#f7901e]" /> Execution Logs
              </h4>
              <div className="bg-black/90 p-3 rounded border border-slate-800 font-mono text-[11px] text-emerald-400 max-h-56 overflow-y-auto space-y-1">
                {node.logs && node.logs.length > 0 ? (
                  node.logs.map((log, i) => (
                    <div key={i} className="leading-tight">&gt; {log}</div>
                  ))
                ) : (
                  <div className="text-slate-600 italic">No execution logs for this run.</div>
                )}
              </div>
            </div>
          </div>
        </div>

        <InfoTooltip text="Closes this inspector panel. Does not stop or re-run the skill." wrapperClassName="w-full block">
          <button
            onClick={onClose}
            className="w-full btn-primary py-2 text-sm text-center"
          >
            Close Inspector
          </button>
        </InfoTooltip>
      </div>
    </div>
  );
}
