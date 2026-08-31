import React, { useState } from "react";
import { Sliders, CheckCircle2, Play, RefreshCw, Layers, ArrowDownUp } from "lucide-react";
import InfoTooltip from "./InfoTooltip";

export default function STypeDashboard({ appState, onRunStype, isCalculating }) {
  const currentParams = appState?.current_stype_params || {
    sets: 5,
    percentiles: [20.0, 40.0, 60.0, 80.0],
    aggregation_field: "d1_Ranking",
    aggregation_type: "GRADE",
    grade_aggregation_method: "weighted_average",
    flex_rules: []
  };

  const [aggField, setAggField] = useState(currentParams.aggregation_field);
  const [aggType, setAggType] = useState(currentParams.aggregation_type);
  const [gradeAggMethod, setGradeAggMethod] = useState(currentParams.grade_aggregation_method || "weighted_average");
  const [numSets, setNumSets] = useState(currentParams.sets || 5);
  const [customPercentiles, setCustomPercentiles] = useState(currentParams.percentiles.join(", "));
  const [flexRules, setFlexRules] = useState(currentParams.flex_rules || []);

  const handleFlexOrderChange = (idx, newOrder) => {
    const updated = [...flexRules];
    updated[idx].flex_order = parseInt(newOrder) || 0;
    setFlexRules(updated);
  };

  const handleFlexOptionChange = (idx, newOption) => {
    const updated = [...flexRules];
    updated[idx].flex_option = newOption;
    setFlexRules(updated);
  };

  const handleSetsChange = (sets) => {
    const val = parseInt(sets);
    setNumSets(val);
    const step = 100 / val;
    const percs = [];
    for (let p = step; p < 100; p += step) {
      percs.push(Math.round(p));
    }
    setCustomPercentiles(percs.join(", "));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const parsedPercentiles = customPercentiles
      .split(",")
      .map(s => parseFloat(s.trim()))
      .filter(n => !isNaN(n) && n > 0 && n < 100);

    onRunStype({
      sets: numSets,
      percentiles: parsedPercentiles.length ? parsedPercentiles : [20.0, 40.0, 60.0, 80.0],
      aggregation_field: aggField,
      aggregation_type: aggType,
      grade_aggregation_method: gradeAggMethod,
      flex_rules: flexRules
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold title-orange">Stage 2: S-Type Parameter Tuning</h2>
          <p className="subtitle-teal text-sm">
            Adjust percentile intervals, ranking drivers, and dimension flex rules to optimize bin reduction.
          </p>
        </div>
        <InfoTooltip text="Runs the N-dimensional S-Type bin collapse for every percentile cut below, using the current aggregation driver and flex rules. Only re-executes the downstream S-Type, audit, and export nodes - the M-Type baseline is not recalculated." position="left">
          <button
            type="submit"
            disabled={isCalculating}
            className="btn-primary px-6 py-2.5 flex items-center gap-2 text-sm"
          >
            {isCalculating ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Calculating Reduction...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Execute S-Type Reduction</span>
              </>
            )}
          </button>
        </InfoTooltip>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Col: Aggregation Drivers */}
        <div className="app-card p-5 space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-200 pb-2">
            1. Aggregation Driver
          </h3>

          <div>
            <InfoTooltip text="The dimension/field whose per-bin value is used to decide which bins are 'low value' and eligible for collapsing during S-Type reduction.">
              <label className="block text-xs font-semibold text-slate-700 mb-1 cursor-help w-fit">
                STYPE Aggregation Field
              </label>
            </InfoTooltip>
            <select
              value={aggField}
              onChange={(e) => setAggField(e.target.value)}
              className="w-full bg-white border border-black rounded px-3 py-2 text-sm text-slate-900 font-mono focus:ring-2 focus:ring-[#ea580c]"
            >
              {(appState?.available_dimensions || ["d1_Ranking"]).map((dim) => (
                <option key={dim} value={dim}>{dim}</option>
              ))}
            </select>
          </div>

          <div>
            <InfoTooltip text="Chooses whether bins are ranked by the aggregation field's grade (see Grade Ranking Basis below) or by summed mass/tonnage.">
              <label className="block text-xs font-semibold text-slate-700 mb-1 cursor-help w-fit">
                STYPE Aggregation Type
              </label>
            </InfoTooltip>
            <div className="grid grid-cols-2 gap-2">
              <InfoTooltip text="Rank and threshold bins using the selected aggregation field's grade. Choose the exact averaging method below.">
                <button
                  type="button"
                  onClick={() => setAggType("GRADE")}
                  className={`w-full py-2 text-xs font-bold rounded border transition ${
                    aggType === "GRADE"
                      ? "bg-[#0a192f] text-white border-black"
                      : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                  }`}
                >
                  GRADE (Weighted)
                </button>
              </InfoTooltip>
              <InfoTooltip text="Rank and threshold bins by their summed mass/tonnage instead of grade - bins with the least material are collapsed first.">
                <button
                  type="button"
                  onClick={() => setAggType("QUANTITY")}
                  className={`w-full py-2 text-xs font-bold rounded border transition ${
                    aggType === "QUANTITY"
                      ? "bg-[#0a192f] text-white border-black"
                      : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                  }`}
                >
                  QUANTITY (Summed)
                </button>
              </InfoTooltip>
            </div>
          </div>

          {aggType === "GRADE" && (
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Grade Ranking Basis
              </label>
              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  onClick={() => setGradeAggMethod("weighted_average")}
                  className={`py-2 px-2 text-xs font-bold rounded border transition text-left ${
                    gradeAggMethod === "weighted_average"
                      ? "bg-[#0d9488] text-white border-black"
                      : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                  }`}
                >
                  Weighted Average (grade concentration)
                  <div className="font-normal text-[10px] opacity-80 mt-0.5">
                    Ranks bins by grade regardless of tonnage. A small, high-grade bin can outrank a large, lower-grade one.
                  </div>
                </button>
                <button
                  type="button"
                  onClick={() => setGradeAggMethod("weighted_sum")}
                  className={`py-2 px-2 text-xs font-bold rounded border transition text-left ${
                    gradeAggMethod === "weighted_sum"
                      ? "bg-[#0d9488] text-white border-black"
                      : "bg-white text-slate-700 border-slate-400 hover:bg-slate-100"
                  }`}
                >
                  Weighted Sum (total contained metal)
                  <div className="font-normal text-[10px] opacity-80 mt-0.5">
                    Ranks bins by total metal content (grade x tonnes). Matches legacy phase_file_generator.py behavior; a bin needs both grade and tonnage to rank highly.
                  </div>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Middle Col: Percentiles Control */}
        <div className="app-card p-5 space-y-4">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-200 pb-2">
            2. Percentile Intervals
          </h3>

          <div>
            <div className="flex justify-between items-center mb-1">
              <InfoTooltip text="Auto-generates evenly-spaced percentile cuts below (e.g. 5 sets = 20/40/60/80%). Overwrites whatever is currently in the Active Percentile Cuts field.">
                <label className="text-xs font-semibold text-slate-700 cursor-help">Preset S-Type Sets ({numSets})</label>
              </InfoTooltip>
              <span className="text-xs text-[#0d9488] font-bold">100 / {numSets} = {100 / numSets}% steps</span>
            </div>
            <InfoTooltip text="Drag to change how many evenly-spaced percentile sets to generate, from 2 up to 10." wrapperClassName="w-full block">
              <input
                type="range"
                min="2"
                max="10"
                value={numSets}
                onChange={(e) => handleSetsChange(e.target.value)}
                className="w-full accent-[#ea580c]"
              />
            </InfoTooltip>
          </div>

          <div>
            <InfoTooltip text="The exact percentile thresholds S-Type reduction will run at. Each value produces its own separate set of collapsed phase files - bins at or below this percentile are flagged for collapse.">
              <label className="block text-xs font-semibold text-slate-700 mb-1 cursor-help w-fit">
                Active Percentile Cuts (%)
              </label>
            </InfoTooltip>
            <input
              type="text"
              value={customPercentiles}
              onChange={(e) => setCustomPercentiles(e.target.value)}
              placeholder="e.g. 20, 40, 60, 80"
              className="w-full bg-white border border-black rounded px-3 py-2 text-sm font-mono text-slate-900 focus:ring-2 focus:ring-[#ea580c]"
            />
            <p className="text-[11px] text-slate-500 mt-1">Comma-separated percentile cuts to generate.</p>
          </div>
        </div>

        {/* Right Col: Summary Overview */}
        <div className="app-card p-5 space-y-3 bg-slate-100">
          <h3 className="font-bold text-base text-slate-900 border-b border-slate-300 pb-2">
            Configuration Notes
          </h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            <strong className="text-slate-900">Flexing Mechanics:</strong> Bins falling below each percentile threshold are flagged and merged into neighboring bins using your Flex Rules.
          </p>
          <ul className="text-xs text-slate-600 space-y-1 list-disc list-inside">
            <li><span className="font-semibold text-slate-900">FLEX UP:</span> Merges into higher bin interval.</li>
            <li><span className="font-semibold text-slate-900">FLEX DOWN:</span> Merges into lower bin interval.</li>
            <li><span className="font-semibold text-slate-900">STATIC:</span> Preserves exact bin selectivity.</li>
          </ul>
        </div>
      </div>

      {/* Interactive Flex Order & Options Table */}
      <div className="app-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-base text-slate-900">3. Interactive Dimension Flex Table</h3>
            <p className="subtitle-teal text-xs">Define priority sequence and flexing direction for each dimension</p>
          </div>
          <span className="text-xs font-semibold bg-[#0a192f] text-white px-3 py-1 rounded">
            {flexRules.length} Configured Dimensions
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#0a192f] text-white text-xs uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3 rounded-tl">
                  <InfoTooltip text="A Cut-Off Grade dimension configured in the COG_Bins sheet (e.g. grade, deleterious element, rock type)." position="bottom">
                    <span className="cursor-help">Dimension Field</span>
                  </InfoTooltip>
                </th>
                <th className="px-4 py-3">
                  <InfoTooltip text="Sets the order dimensions are tried when searching for a bin to merge a collapsed bin into. Lower numbers are tried first; 0 means this dimension is ignored during the search." position="bottom">
                    <span className="cursor-help">Flex Order Priority</span>
                  </InfoTooltip>
                </th>
                <th className="px-4 py-3">
                  <InfoTooltip text="FLEX UP merges a collapsed bin into the next higher interval on this dimension, FLEX DOWN into the next lower interval, and STATIC never collapses this dimension's boundary." position="bottom">
                    <span className="cursor-help">Flex Direction Rule</span>
                  </InfoTooltip>
                </th>
                <th className="px-4 py-3 rounded-tr">
                  <InfoTooltip text="Whether this dimension currently takes part in the bin-collapse search (Priority greater than 0) or is bypassed entirely (Priority = 0)." position="bottom">
                    <span className="cursor-help">Status</span>
                  </InfoTooltip>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-300 bg-white">
              {flexRules.map((rule, idx) => (
                <tr key={rule.fieldname} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono font-bold text-slate-900">
                    {rule.fieldname}
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="number"
                      min="0"
                      max="10"
                      value={rule.flex_order}
                      onChange={(e) => handleFlexOrderChange(idx, e.target.value)}
                      className="w-20 bg-slate-50 border border-black rounded px-2 py-1 text-sm font-bold text-slate-900 text-center"
                    />
                    <span className="text-xs text-slate-500 ml-2">
                      {rule.flex_order === 0 ? "(Ignored)" : `Priority ${rule.flex_order}`}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={rule.flex_option}
                      onChange={(e) => handleFlexOptionChange(idx, e.target.value)}
                      className="bg-slate-50 border border-black rounded px-3 py-1.5 text-xs font-bold text-slate-900"
                    >
                      <option value="FLEX DOWN">FLEX DOWN (Collapse to lower)</option>
                      <option value="FLEX UP">FLEX UP (Collapse to upper)</option>
                      <option value="STATIC">STATIC (Do not collapse)</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 text-xs">
                    {rule.flex_order > 0 ? (
                      <span className="text-emerald-700 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Active in Collapse
                      </span>
                    ) : (
                      <span className="text-slate-400 font-medium">Bypassed (0)</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </form>
  );
}
