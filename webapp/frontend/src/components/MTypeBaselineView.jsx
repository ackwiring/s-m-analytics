import React from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { Layers, Database, Sparkles, Scale, Grid, ArrowRight, UploadCloud } from "lucide-react";
import InfoTooltip from "./InfoTooltip";


export default function MTypeBaselineView({ appState, onProceedToStype, onUploadBlockModel }) {
  const mtype = appState?.mtype_baseline;

  if (!mtype) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 1: Base M-Type Analysis</h2>
          <p className="subtitle-teal text-sm">
            Configuration loaded: <span className="font-mono text-slate-900 font-semibold">{appState?.config_name || "None"}</span>. Awaiting Block Model dataset to execute baseline slicing.
          </p>
        </div>

        {/* Empty State / Ingestion Prompt */}
        <div className="app-card p-12 text-center space-y-5 bg-slate-50">
          <div className="w-16 h-16 bg-white border-2 border-black rounded-full flex items-center justify-center mx-auto text-[#f7901e]">
            <Database className="w-8 h-8" />
          </div>
          <div className="max-w-md mx-auto space-y-2">
            <h3 className="text-xl font-bold text-slate-900">No Block Model Data Loaded</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Drag and drop your genuine reserve block model (<code className="bg-slate-200 px-1 py-0.5 rounded font-mono">.csv</code> or <code className="bg-slate-200 px-1 py-0.5 rounded font-mono">.parquet</code>) onto the screen, or browse below to execute 1D M-Type binning and N-D S-Type reduction.
            </p>
          </div>

          <div className="flex items-center justify-center gap-4 pt-2">
            <InfoTooltip text="Opens a file picker to select your genuine reserve block model. Triggers ingestion and 1D M-Type baseline binning using the already-loaded config workbook.">
              <label className="btn-primary px-6 py-2.5 cursor-pointer text-sm flex items-center gap-2">
                <UploadCloud className="w-4 h-4" />
                <span>Select Block Model (.csv)</span>
                <input
                  type="file"
                  className="hidden"
                  accept=".csv,.parquet,.txt"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file && onUploadBlockModel) onUploadBlockModel(file);
                  }}
                />
              </label>
            </InfoTooltip>
          </div>
        </div>

        {/* Configuration Overview */}
        <div className="grid grid-cols-2 gap-6">
          <div className="app-card p-5">
            <h3 className="font-bold text-sm text-slate-900 mb-2">Configured Cut-Off Grade Dimensions</h3>
            <div className="space-y-1.5">
              {(appState?.available_dimensions || []).map((dim) => (
                <div key={dim} className="app-card-sm p-2 text-xs font-mono text-slate-700">
                  {dim}
                </div>
              ))}
            </div>
          </div>

          <div className="app-card p-5">
            <h3 className="font-bold text-sm text-slate-900 mb-2">Weighted Fields & Mass Drivers</h3>
            <div className="space-y-1.5">
              {(appState?.available_weighted_fields || []).map((wf) => (
                <div key={wf.field} className="app-card-sm p-2 flex justify-between text-xs">
                  <span className="font-mono text-slate-700">{wf.field}</span>
                  <span className="text-slate-500 font-mono">Weight: {wf.weighting}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  const chartData = (mtype.bin_distribution || []).map(b => ({
    name: `Bin ${b.bin_id}`,
    mass: b.mass,
    percentage: b.percentage
  }));


  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 1: Base M-Type Analysis</h2>
          <p className="subtitle-teal text-sm">
            Unreduced 1-Dimensional Cut-Off Grade (COG) baseline calculated directly from the block model.
          </p>
        </div>
        <InfoTooltip text="Moves to Stage 2, where you set percentile cuts, choose the grade/quantity ranking driver, and configure flex rules for N-dimensional S-Type bin collapsing." position="left">
          <button
            onClick={onProceedToStype}
            className="btn-primary px-5 py-2.5 flex items-center gap-2 text-sm"
          >
            <span>Tune S-Type Parameters</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </InfoTooltip>
      </div>

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <InfoTooltip text="Sum of the mass/tonnage field across every block in the uploaded model - the total reserve before any binning or reduction." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              <Scale className="w-4 h-4 text-[#f7901e]" /> Total Reserve Mass
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {mtype.total_mass.toLocaleString()} <span className="text-xs font-normal text-slate-600">Tonnes</span>
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text="Count of distinct multi-dimensional Cut-Off Grade bins produced by the unreduced M-Type baseline, before S-Type collapsing removes any of them." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              <Grid className="w-4 h-4 text-[#00a3a6]" /> Total Active Bins
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {mtype.total_bins} <span className="text-xs font-normal text-slate-600">Discrete Bins</span>
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text="The distinct mine phases/pits present in the uploaded block model that phase files will be generated for." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              <Layers className="w-4 h-4 text-[#f7901e]" /> Active Phases
            </div>
            <div className="text-xl font-bold text-slate-900 truncate">
              {mtype.phases.join(", ") || "None"}
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text="Number of Cut-Off Grade dimensions configured in the COG_Bins sheet (e.g. grade, deleterious elements) that the block model is binned across." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4 text-[#00a3a6]" /> Dimension Fields
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {mtype.dimension_count} <span className="text-xs font-normal text-slate-600">COG Dimensions</span>
            </div>
          </div>
        </InfoTooltip>
      </div>

      {/* Main Content Grid: Chart & Weighted Grades */}
      <div className="grid grid-cols-3 gap-6">
        {/* Baseline Bin Distribution Chart */}
        <div className="col-span-2 app-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Baseline Bin Mass Distribution</h3>
              <p className="text-xs subtitle-teal">Unreduced mass distribution across discrete COG intervals</p>
            </div>
            <span className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-200 border border-slate-800">
              {mtype.total_bins} Bins Sliced
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="name" stroke="#475569" fontSize={11} interval={0} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip 
                  formatter={(val) => [`${val.toLocaleString()} Tonnes`, "Mass"]}
                  contentStyle={{ backgroundColor: "#0f172a", border: "1.5px solid black", borderRadius: "6px", color: "#fff" }}
                />
                <Bar dataKey="mass" fill="#f7901e" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Weighted Grades Table */}
        <div className="app-card p-6 flex flex-col justify-between">
          <div>
            <InfoTooltip text="Each field's grade averaged across the whole reserve, weighted by its designated tonnage/mass field (from the WeightedFields config sheet) rather than a simple unweighted mean.">
              <h3 className="font-bold text-base text-slate-900 mb-1 cursor-help">Weighted Head Grades</h3>
            </InfoTooltip>
            <p className="text-xs subtitle-teal mb-4">Calculated against designated mass weightings</p>

            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {Object.entries(mtype.weighted_summary || {}).map(([field, val]) => (
                <div key={field} className="app-card-sm p-2.5 flex items-center justify-between">
                  <span className="text-xs font-mono font-medium text-slate-700 truncate mr-2" title={field}>
                    {field}
                  </span>
                  <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-300">
                    {val}
                  </span>
                </div>
              ))}
              {Object.keys(mtype.weighted_summary || {}).length === 0 && (
                <div className="text-xs text-slate-500 italic p-4 text-center">No weighted grade fields configured.</div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-300 text-xs text-slate-600">
            <span className="font-semibold text-slate-900">Next Step:</span> Proceed to the S-Type dashboard to collapse low-priority bins.
          </div>
        </div>
      </div>
    </div>
  );
}
