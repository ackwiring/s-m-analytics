import numpy as np
import pandas as pd

from skills.mtype_baseline.skill import MTypeBaselineSkill


def _real_cog_bins_shape():
    # Mirrors the production COG_Bins schema exactly: 'MIN'/'MAX' string
    # sentinels in COG_CUTOFF/COG_TOP, real column names (underscore, not
    # space). This is the exact shape that crashed before the 2026-09-01
    # fix - first with KeyError('COG CUTOFF') from a column-name typo, then
    # with TypeError('<' not supported between int and str) because the
    # 'MIN' sentinel was never resolved to a number before being used as a
    # pd.cut() bin edge.
    return pd.DataFrame({
        "FIELDNAME": ["d1_Ranking"] * 3,
        "INTERVAL": [1, 2, 3],
        "COG_CUTOFF": ["MIN", 100, 200],
        "COG_TOP": [100, 200, "MAX"],
        "STYPE OPTION": ["STATIC", "FLEX DOWN", "FLEX DOWN"],
    })


def test_dcog_handles_real_min_max_sentinel_schema():
    cog_bins = _real_cog_bins_shape()
    df = pd.DataFrame({"d1_Ranking": [5.0, 50.0, 150.0, 250.0], "MASS": [10, 20, 30, 40]})

    skill = MTypeBaselineSkill()
    skill.dcog(df, cog_bins)  # mutates df in place, adding d1_Ranking_BIN

    assert "d1_Ranking_BIN" in df.columns
    # value below the first numeric cutoff (100) must fall in bin 1, not
    # error out or get silently dropped - this is exactly what the 'MIN'
    # sentinel resolution has to get right.
    assert df.loc[df["d1_Ranking"] == 5.0, "d1_Ranking_BIN"].iloc[0] == 1
    assert df.loc[df["d1_Ranking"] == 250.0, "d1_Ranking_BIN"].iloc[0] == 3


def test_mtype_baseline_matches_reference_binning_on_synthetic_data():
    # Regression pin for the 2026-09-01 reconciliation against
    # phase_file_generator.py's dcog()+bin_data() (the legacy reference
    # implementation) on identical synthetic input: same seed, same COG_Bins
    # shape as the real PhaseCalculator_V3 workbook. Total mass and bin
    # count were verified by hand to match the legacy script's output
    # (1104169.01 total mass, 152 unique bins, 100% row-level per-dimension
    # agreement across all 4 dimensions) - this test pins the mass/bin-count
    # half of that so a future change can't silently regress it back to
    # disagreeing with the legacy implementation.
    cog_bins = pd.DataFrame({
        "FIELDNAME": (
            ["d1_Ranking"] * 5 + ["d2_CSRRanking"] * 4 +
            ["d3_CVRanking"] * 3 + ["d4_CASHRanking"] * 3
        ),
        "INTERVAL": [1, 2, 3, 4, 5, 1, 2, 3, 4, 1, 2, 3, 1, 2, 3],
        "COG_CUTOFF": ["MIN", 100000, 150000, 200000, 250000, "MIN", 40, 55, 68, "MIN", 22, 24, "MIN", -13, -10.6],
        "COG_TOP": [100000, 150000, 200000, 250000, "MAX", 40, 55, 68, "MAX", 22, 24, "MAX", -13, -10.6, "MAX"],
        "STYPE OPTION": ["STATIC"] + ["FLEX DOWN"] * 14,
    })

    rng = np.random.default_rng(42)
    n = 2000
    df = pd.DataFrame({
        "d1_Ranking": rng.uniform(50000, 300000, n),
        "d2_CSRRanking": rng.uniform(10, 80, n),
        "d3_CVRanking": rng.uniform(10, 40, n),
        "d4_CASHRanking": rng.uniform(-50, 50, n),
        "MASS": rng.uniform(100, 1000, n),
    })

    skill = MTypeBaselineSkill()
    result_cog = skill.dcog(df, cog_bins)
    binned = skill.bin_data(df, result_cog)

    assert abs(float(binned["MASS"].sum()) - 1104169.01) < 1.0
    assert binned["BIN"].nunique() == 152
