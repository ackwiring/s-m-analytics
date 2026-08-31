import React, { useState } from "react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { BarChart3, TrendingDown, CheckCircle, Percent, ArrowRight } from "lucide-react";
import InfoTooltip from "./InfoTooltip";

export default function ComparisonView({ appState, onProceedToExport }) {
  const mtype = appState?.mtype_baseline;
  const stypeResults = appState?.stype_results || [];

  const [selectedPerc, setSelectedPerc] = useState(
    stypeResults.length ? stypeResults[0].percentile : 20.0
  );

  const activeStype = stypeResults.find(r => r.percentile === selectedPerc) || stypeResults[0];

  if (!mtype || !activeStype) {
    return (
      <div className="app-card p-12 text-center">
        <p className="text-slate-600">Please run the S-Type calculation first to view comparative analytics.</p>
      </div>
    );
  }

  // Build combined chart data
  const mtypeDist = mtype.bin_distribution || [];
  const stypeDist = activeStype.bin_distribution || [];

  const chartData = stypeDist.map(b => {
    const orig = mtypeDist.find(m => m.bin_id === b.bin_id);
    return {
      bin: `Bin ${b.bin_id}`,
      Reduced: b.mass,
      Original: orig ? orig.mass : 0,
    };
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 3: Comparative Analysis</h2>
          <p className="subtitle-teal text-sm">
            Evaluate bin collapsing effectiveness and grade preservation across percentiles.
          </p>
        </div>
        <InfoTooltip text="Moves to Stage 4 to download a ZIP of the M-Type and S-Type phase files and audit reports for the currently calculated percentile runs." position="left">
          <button
            onClick={onProceedToExport}
            className="btn-primary px-5 py-2.5 flex items-center gap-2 text-sm"
          >
            <span>Export Phase Files</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </InfoTooltip>
      </div>

      {/* Percentile Selector Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-300 pb-3">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-wider mr-2">Select Percentile:</span>
        {stypeResults.map((res) => (
          <InfoTooltip key={res.percentile} text={`Show the bin collapse and grade preservation results for the ${res.percentile}% S-Type cut - bins at or below this percentile were flagged and merged.`}>
            <button
              onClick={() => setSelectedPerc(res.percentile)}
              className={`px-4 py-1.5 text-xs font-bold rounded-md border transition ${
                selectedPerc === res.percentile
                  ? "bg-[#ea580c] text-white border-black"
                  : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
              }`}
            >
              {res.percentile}% S-Type
            </button>
          </InfoTooltip>
        ))}
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-4 gap-4">
        <InfoTooltip text="Number of discrete N-dimensional bins in the unreduced M-Type baseline, before this percentile's S-Type collapse was applied." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Original Bins
            </div>
            <div className="text-2xl font-bold text-slate-900">
              {activeStype.original_bins_count} <span className="text-xs font-normal text-slate-500">Bins</span>
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text={`Number of bins remaining after collapsing bins at or below the ${activeStype.percentile}% threshold into their flex-rule neighbors.`} wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Reduced Bins ({activeStype.percentile}%)
            </div>
            <div className="text-2xl font-bold text-[#ea580c]">
              {activeStype.reduced_bins_count} <span className="text-xs font-normal text-slate-500">Remaining</span>
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text="Percentage decrease in bin count from Original Bins to Reduced Bins - higher means more aggressive collapsing at this percentile cut." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
              <TrendingDown className="w-4 h-4 text-emerald-600" /> Bin Reduction
            </div>
            <div className="text-2xl font-bold text-emerald-600">
              {activeStype.reduction_pct}% <span className="text-xs font-normal text-slate-500">Reduction</span>
            </div>
          </div>
        </InfoTooltip>

        <InfoTooltip text="Share of total reserve mass still accounted for after collapsing bins. S-Type collapsing merges bins rather than discarding material, so this should always read 100%." wrapperClassName="w-full block">
          <div className="app-card p-4">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1">
              <CheckCircle className="w-4 h-4 text-[#0d9488]" /> Mass Preservation
            </div>
            <div className="text-2xl font-bold text-slate-900">
              100.0% <span className="text-xs font-normal text-slate-500">Preserved</span>
            </div>
          </div>
        </InfoTooltip>
      </div>

      {/* Side by Side Chart & Grade Deltas */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 app-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-slate-900">Bin Collapsing Comparison ({activeStype.percentile}% Cut)</h3>
              <p className="subtitle-teal text-xs">Visualizing original vs collapsed bin distribution</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#cbd5e1" />
                <XAxis dataKey="bin" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "#0f172a", border: "1.5px solid black", borderRadius: "6px", color: "#fff" }}
                />
                <Legend />
                <Bar dataKey="Original" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Reduced" fill="#ea580c" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Grade Preservation Deltas */}
        <div className="app-card p-6 space-y-4">
          <div>
            <InfoTooltip text="Percentage change in each field's weighted-average grade after S-Type collapsing, versus its value in the unreduced M-Type baseline. Green means the shift is under 0.5% (negligible); amber flags a larger drift worth reviewing before export.">
              <h3 className="font-bold text-base text-slate-900 mb-1 cursor-help w-fit">Grade Variance Check</h3>
            </InfoTooltip>
            <p className="subtitle-teal text-xs">Variance (% Delta) from Baseline M-Type</p>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
            {Object.entries(activeStype.grade_preservation || {}).map(([field, delta]) => (
              <div key={field} className="app-card-sm p-3 flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-800 truncate mr-2" title={field}>
                  {field}
                </span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded border ${
                  Math.abs(delta) < 0.5 
                    ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                    : "bg-amber-100 text-amber-800 border-amber-300"
                }`}>
                  {delta > 0 ? `+${delta}%` : `${delta}%`}
                </span>
              </div>
            ))}
            {Object.keys(activeStype.grade_preservation || {}).length === 0 && (
              <div className="text-xs text-slate-500 italic p-4 text-center">0.0% variance across all fields.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
