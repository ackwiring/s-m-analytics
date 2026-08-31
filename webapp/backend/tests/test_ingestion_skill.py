import math

from orchestrator.context import WorkflowContext
from skills.ingestion.skill import IngestionSkill


def test_cp1252_bytes_decode_correctly_not_via_latin1_first():
    # 0x92 is cp1252's right single quotation mark (') - but it's also a
    # "valid" (if meaningless, a C1 control char) latin-1 byte. This is the
    # exact bug the encoding-order fix guards against: latin-1 never raises a
    # decode error, so trying it before cp1252 means it always "wins" and
    # silently produces the wrong character instead of falling through to the
    # encoding that's actually correct for Windows-exported CSVs.
    csv_bytes = b"id,note\n1,Site A" + bytes([0x92]) + b"s pit"

    skill = IngestionSkill()
    ctx = WorkflowContext()
    result = skill.run(ctx, {"dataset_source": csv_bytes, "dataset_name": "test.csv"})

    assert result.success, result.error
    assert ctx.block_model_df is not None
    note = ctx.block_model_df.loc[0, "note"]
    assert note == "Site A’s pit"
    assert any("cp1252" in log for log in result.logs)


def test_utf8_sig_bom_is_stripped():
    csv_bytes = "id,value\n1,42".encode("utf-8-sig")

    skill = IngestionSkill()
    ctx = WorkflowContext()
    result = skill.run(ctx, {"dataset_source": csv_bytes, "dataset_name": "test.csv"})

    assert result.success, result.error
    # A leading BOM that survives decoding shows up as a mangled first
    # column name (e.g. "﻿id") - assert it's actually gone.
    assert list(ctx.block_model_df.columns) == ["id", "value"]


def test_minus_99_sentinel_only_nulled_in_numeric_columns():
    csv_bytes = b"grade,label\n-99,-99\n1.5,Sample-99"

    skill = IngestionSkill()
    ctx = WorkflowContext()
    result = skill.run(ctx, {"dataset_source": csv_bytes, "dataset_name": "test.csv"})

    assert result.success, result.error
    df = ctx.block_model_df
    # Numeric sentinel -> NaN, as intended.
    assert math.isnan(df.loc[0, "grade"])
    # The same literal value in a text column must survive untouched -
    # this is what the old whole-dataframe .replace() would have nulled.
    assert df.loc[0, "label"] == "-99"
    assert df.loc[1, "label"] == "Sample-99"
