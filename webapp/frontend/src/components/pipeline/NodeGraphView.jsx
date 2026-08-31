import React, { useState } from "react";
import { CheckCircle2, Clock, Play, ArrowRight, FileText, Database, ShieldAlert, Cpu, Terminal } from "lucide-react";
import InfoTooltip from "../InfoTooltip";

export default function NodeGraphView({ appState, onInspectNode }) {
  const nodes = appState?.pipeline_nodes || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Modular Workflow Pipeline</h2>
          <p className="subtitle-teal text-sm">
            n8n-style DAG orchestrator executing autonomous specialized skills in sequence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-[#0a192f] text-slate-200 border border-black px-3 py-1.5 rounded-md flex items-center gap-1.5 font-mono">
            <Cpu className="w-3.5 h-3.5 text-[#ea580c]" />
            Orchestrator v2.0 Active
          </span>
        </div>
      </div>

      {/* DAG Flow Visualizer */}
      <div className="app-card p-6 bg-slate-900 border-2 border-black text-white">
        <div className="flex items-center justify-between overflow-x-auto pb-4 gap-3">
          {nodes.map((node, idx) => {
            const isCompleted = node.status === "COMPLETED";
            const isRunning = node.status === "RUNNING";
            const isError = node.status === "ERROR";

            return (
              <React.Fragment key={node.name}>
                {/* Node Box */}
                <InfoTooltip text={`Click to open the inspector for this skill: its identifier, version, execution status/timing, and full console logs. Currently: ${node.status}.`} wrapperClassName="flex-1 min-w-[180px]">
                  <div
                    onClick={() => onInspectNode(node)}
                    className={`w-full h-full p-4 rounded-md border-2 cursor-pointer transition-all hover:scale-102 ${
                      isCompleted
                        ? "bg-slate-800/90 border-emerald-500"
                        : isRunning
                        ? "bg-slate-800 border-[#ea580c] animate-pulse"
                        : isError
                        ? "bg-red-950/80 border-red-500"
                        : "bg-slate-800/40 border-slate-700 opacity-60"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-[#0d9488]">
                        {node.category}
                      </span>
                      <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                        isCompleted ? "bg-emerald-950 text-emerald-300 border border-emerald-700" :
                        isRunning ? "bg-amber-950 text-amber-300 border border-amber-700" :
                        isError ? "bg-red-900 text-red-200" : "bg-slate-700 text-slate-300"
                      }`}>
                        {node.status}
                      </span>
                    </div>

                    <h4 className="font-bold text-sm text-slate-100 mb-1 leading-snug">{node.display_name}</h4>
                    <p className="text-[11px] text-slate-400 line-clamp-2 mb-3">{node.description}</p>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-700/80 pt-2">
                      <span className="flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {node.timing_ms > 0 ? `${node.timing_ms}ms` : "0ms"}
                      </span>
                      <span className="text-slate-400 hover:text-white underline">Inspect &rarr;</span>
                    </div>
                  </div>
                </InfoTooltip>

                {/* Arrow Connector */}
                {idx < nodes.length - 1 && (
                  <div className="text-slate-500 flex items-center justify-center">
                    <ArrowRight className="w-5 h-5 text-[#ea580c]" />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Execution Highlights */}
      <div className="grid grid-cols-3 gap-6">
        <div className="app-card p-5">
          <h3 className="font-bold text-sm text-slate-900 mb-2">Decoupled Skill Runtime</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Each skill runs as an isolated, deterministic execution block. When you adjust S-Type percentiles, the orchestrator only re-executes the downstream S-Type and Audit nodes, bypassing M-Type re-slicing.
          </p>
        </div>

        <div className="app-card p-5">
          <h3 className="font-bold text-sm text-slate-900 mb-2">Zero Mutable State Leaks</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Shared variables are passed exclusively through the strongly-typed <code className="bg-slate-200 px-1 py-0.5 rounded font-mono">WorkflowContext</code>. Upstream data cannot be corrupted by downstream transformations.
          </p>
        </div>

        <div className="app-card p-5">
          <h3 className="font-bold text-sm text-slate-900 mb-2">Observable Logs & Tracing</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Click on any skill block above to inspect its live console logs, input parameters, execution latency, and intermediate output data.
          </p>
        </div>
      </div>
    </div>
  );
}
