import React from "react";
import { Layers, Sliders, BarChart3, Download, FileText, Database, ShieldCheck, Trash2, Workflow } from "lucide-react";
import InfoTooltip from "./InfoTooltip";
import qsLogo from "../assets/qs_logo.png";

export default function Sidebar({ activeTab, setActiveTab, appState, onClearDataset, onClearConfig }) {
  const tabs = [
    { id: "pipeline", label: "0. Workflow Pipeline", icon: Workflow, desc: "Modular DAG Skills", tip: "View the orchestrator's DAG of skills, their run status, timing, and console logs for the current pipeline execution." },
    { id: "mtype", label: "1. Base M-Type Baseline", icon: Layers, desc: "Standard 1D Cutoff Bins", tip: "View the unreduced 1-dimensional Cut-Off Grade baseline calculated directly from the uploaded block model, before any S-Type collapsing." },
    { id: "stype", label: "2. S-Type Parameter Tuning", icon: Sliders, desc: "Percentiles & Flex Rules", tip: "Configure percentile cuts, the grade/quantity ranking driver, and per-dimension flex rules, then run the N-dimensional S-Type bin reduction." },
    { id: "comparison", label: "3. Comparative Analytics", icon: BarChart3, desc: "Bin Reduction & Preservation", tip: "Compare the reduced S-Type bin distribution against the original M-Type baseline at each percentile cut, and check grade preservation." },
    { id: "export", label: "4. Export Phase Files", icon: Download, desc: "COMET Package Download", tip: "Download a ZIP bundle of COMET-ready M-Type and S-Type phase files plus audit reports." },
  ];

  const appName = appState?.app_name || "M & S Type Analyzer";
  const appVersion = appState?.app_version || "v2.0.0";
  const hasLoadedDataset = appState?.mtype_baseline !== null && appState?.dataset_name !== "No Block Model Loaded";
  const hasLoadedConfig = !!appState?.config_name && appState.config_name !== "None";

  const handleDeleteConfig = () => {
    if (window.confirm("Remove the config workbook from the active workspace? This also clears the loaded block model dataset and every calculated result, since they depend on this config. Files on disk are not affected.")) {
      onClearConfig();
    }
  };

  const handleDeleteDataset = () => {
    if (window.confirm("Remove the block model dataset from the active workspace? The config workbook stays loaded. Files on disk are not affected.")) {
      onClearDataset();
    }
  };

  return (
    <aside className="w-72 bg-[#0a192f] text-slate-200 flex flex-col justify-between border-r-2 border-black flex-shrink-0 h-screen sticky top-0">
      <div>
        {/* App Branding: Single QS Corporate Logo */}
        <div className="p-5 border-b border-slate-800 bg-[#081224]">
          <div className="flex items-center gap-3">
            <img
              src={qsLogo}
              alt="Quantified Strategies"
              className="h-8 w-auto object-contain flex-shrink-0"
            />
            <div className="min-w-0">
              <h1 className="text-lg font-bold text-white tracking-tight leading-tight truncate">
                PhaseAnalyzer
              </h1>
              <p className="text-[11px] font-semibold text-[#00a3a6] uppercase tracking-wider truncate">
                {appName}
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="p-4 space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <InfoTooltip key={tab.id} text={tab.tip} position="right" wrapperClassName="w-full block">
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-start gap-3 p-3 rounded-md border text-left transition-all ${
                    isActive
                      ? "bg-[#1e293b] border-[#f7901e] text-white"
                      : "bg-transparent border-transparent text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  }`}
                >
                  <Icon className={`w-5 h-5 mt-0.5 ${isActive ? "text-[#f7901e]" : "text-[#00a3a6]"}`} />
                  <div>
                    <div className="font-semibold text-sm leading-snug">{tab.label}</div>
                    <div className="text-xs text-slate-400 font-normal">{tab.desc}</div>
                  </div>
                </button>
              </InfoTooltip>
            );
          })}
        </nav>
      </div>

      {/* Active Data Context Status */}
      <div className="p-4 border-t border-slate-800 space-y-3 bg-[#081224]">
        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active Workspace</div>

        <div className="bg-slate-900/90 p-2.5 rounded border border-slate-700 text-xs space-y-2">
          {/* Config File */}
          <div>
            <div className="text-[10px] text-slate-500 font-semibold uppercase">Config Workbook</div>
            <div className="flex items-center justify-between gap-2 mt-0.5">
              <div className="flex items-center gap-2 text-slate-300 truncate min-w-0">
                <FileText className="w-3.5 h-3.5 text-[#f7901e] flex-shrink-0" />
                <span className="truncate font-mono" title={appState?.config_name}>
                  {hasLoadedConfig ? appState.config_name : "No Config Loaded"}
                </span>
              </div>
              {hasLoadedConfig && (
                <InfoTooltip text="Removes the config workbook from the active workspace. Also clears the block model dataset and every calculated result, since they all depend on this config's dimensions and weightings. Does not delete any files on disk." position="left">
                  <button
                    onClick={handleDeleteConfig}
                    aria-label="Delete config workbook from workspace"
                    className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 flex-shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </InfoTooltip>
              )}
            </div>
          </div>

          {/* Dataset File */}
          <div className="pt-1 border-t border-slate-800">
            <div className="text-[10px] text-slate-500 font-semibold uppercase">Block Model Dataset</div>
            <div className="flex items-center justify-between gap-2 mt-0.5">
              <div className="flex items-center gap-2 truncate min-w-0">
                <Database className="w-3.5 h-3.5 text-[#00a3a6] flex-shrink-0" />
                <span className={`truncate font-mono ${hasLoadedDataset ? "text-emerald-300 font-bold" : "text-slate-500 italic"}`} title={appState?.dataset_name}>
                  {appState?.dataset_name || "No Block Model Loaded"}
                </span>
              </div>
              {hasLoadedDataset && (
                <InfoTooltip text="Removes the block model dataset from the active workspace (the config workbook stays loaded). Does not delete any files on disk." position="left">
                  <button
                    onClick={handleDeleteDataset}
                    aria-label="Delete block model dataset from workspace"
                    className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 flex-shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </InfoTooltip>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
          <span className="flex items-center gap-1 truncate" title={`${appName} ${appVersion}`}>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
            <span className="truncate font-semibold">{appName} {appVersion}</span>
          </span>
          <span className="text-slate-500 flex-shrink-0">Port 1943</span>
        </div>
      </div>
    </aside>
  );
}
