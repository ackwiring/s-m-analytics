import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles

from models import STypeParameters, FullAnalysisResponse, MTypeResult, STypePercentileResult, FlexOrderRule, PipelineNodeInfo
from orchestrator.pipeline import PipelineOrchestrator

app = FastAPI(title="M and S Type Reserve Phase Analyzer - Modular Orchestrator", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    # allow_origins="*" + allow_credentials=True is a contradictory pair -
    # Starlette handles it by reflecting the request's Origin back verbatim,
    # which defeats the origin restriction entirely for a service exposed
    # over the Tailscale network. The frontend never sends credentialed
    # requests (no cookies/auth), so there's nothing to gain from it here.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

ORCHESTRATOR = PipelineOrchestrator()

# Initialize default configuration if available
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_EXCEL = os.path.join(ROOT_DIR, "PhaseCalculator_V3_MetCoal_2021-06-03.xlsx")
if not os.path.exists(DEFAULT_EXCEL):
    DEFAULT_EXCEL = os.path.join(ROOT_DIR, "PhaseCalculator_V1_MetCoal_2021-06-03.xlsx")

if os.path.exists(DEFAULT_EXCEL):
    ORCHESTRATOR.run_node("ingestion_config", {
        "config_source": DEFAULT_EXCEL,
        "config_name": os.path.basename(DEFAULT_EXCEL)
    })

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "M & S Type Modular Pipeline Orchestrator"}

@app.get("/api/state", response_model=FullAnalysisResponse)
def get_current_state():
    ctx = ORCHESTRATOR.context
    dims = [str(d) for d in ctx.raw_config['cog_bins']['FIELDNAME'].unique()] if ('cog_bins' in ctx.raw_config) else []
    
    weighted_fields = []
    if 'weighted_fields' in ctx.raw_config:
        for _, r in ctx.raw_config['weighted_fields'].iterrows():
            weighted_fields.append({"field": str(r['Field']), "weighting": str(r['Weighting'])})

    sum_fields = []
    if 'sum_fields' in ctx.raw_config:
        sum_fields = [str(f) for f in ctx.raw_config['sum_fields']['Field'].unique()]

    flex_rules = []
    if 'stype_flexorder' in ctx.raw_config and not ctx.raw_config['stype_flexorder'].empty:
        for _, r in ctx.raw_config['stype_flexorder'].iterrows():
            fieldname = str(r['FIELDNAME']) if 'FIELDNAME' in r else str(r[0])
            flex_order = int(r['Flex Order']) if 'Flex Order' in r else 0
            opt = "STATIC"
            if 'cog_bins' in ctx.raw_config:
                cog = ctx.raw_config['cog_bins']
                sub = cog.query(f"FIELDNAME == '{fieldname}'")
                if not sub.empty and 'STYPE OPTION' in sub.columns:
                    opt = str(sub['STYPE OPTION'].dropna().iloc[0])
            flex_rules.append(FlexOrderRule(fieldname=fieldname, flex_order=flex_order, flex_option=opt))

    stype_params = STypeParameters(
        sets=ctx.raw_config.get('stype_sets', 5),
        percentiles=[20.0, 40.0, 60.0, 80.0],
        aggregation_field=ctx.raw_config.get('stype_agg_field', (dims[0] if dims else 'd1_Ranking')),
        aggregation_type=ctx.raw_config.get('stype_agg_type', 'GRADE'),
        flex_rules=flex_rules
    )

    pipeline_nodes = [PipelineNodeInfo(**n) for n in ORCHESTRATOR.get_pipeline_graph_state()]

    if ctx.block_model_df is None:
        return FullAnalysisResponse(
            status="awaiting_dataset",
            message="Configuration ready. Awaiting Block Model dataset to execute pipeline.",
            dataset_name=ctx.dataset_name,
            config_name=ctx.config_name,
            mtype_baseline=None,
            stype_results=[],
            available_dimensions=dims,
            available_weighted_fields=weighted_fields,
            available_sum_fields=sum_fields,
            current_stype_params=stype_params,
            pipeline_nodes=pipeline_nodes
        )

    stype_results = [STypePercentileResult(**r['payload']) for r in ctx.stype_runs.values()]

    return FullAnalysisResponse(
        status="success",
        message="Orchestrated pipeline completed successfully.",
        dataset_name=ctx.dataset_name,
        config_name=ctx.config_name,
        mtype_baseline=MTypeResult(**ctx.mtype_summary) if ctx.mtype_summary else None,
        stype_results=stype_results,
        available_dimensions=dims,
        available_weighted_fields=weighted_fields,
        available_sum_fields=sum_fields,
        current_stype_params=stype_params,
        pipeline_nodes=pipeline_nodes
    )

@app.post("/api/upload-files")
async def upload_files(
    config_file: Optional[UploadFile] = File(None),
    dataset_file: Optional[UploadFile] = File(None)
):
    try:
        if config_file is not None and config_file.filename:
            contents = await config_file.read()
            ORCHESTRATOR.run_node("ingestion_config", {
                "config_source": contents,
                "config_name": config_file.filename
            })

        if dataset_file is not None and dataset_file.filename:
            contents = await dataset_file.read()
            ORCHESTRATOR.run_node("ingestion_config", {
                "dataset_source": contents,
                "dataset_name": dataset_file.filename
            })
            ORCHESTRATOR.run_pipeline()

        return get_current_state()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Upload processing failed: {str(e)}")

@app.post("/api/run-stype", response_model=FullAnalysisResponse)
def run_stype(params: STypeParameters):
    ctx = ORCHESTRATOR.context
    if ctx.block_model_df is None:
        raise HTTPException(status_code=400, detail="Engine not initialized with data.")

    # Re-run only downstream S-Type, Audit & Export nodes!
    ORCHESTRATOR.run_node("stype_reduction", {
        "percentiles": params.percentiles,
        "aggregation_field": params.aggregation_field,
        "aggregation_type": params.aggregation_type,
        "flex_rules": [r.dict() for r in params.flex_rules]
    })
    ORCHESTRATOR.run_node("audit_verification")
    ORCHESTRATOR.run_node("export_bundle")

    state = get_current_state()
    state.current_stype_params = params
    return state

@app.post("/api/clear-dataset")
def clear_dataset():
    ctx = ORCHESTRATOR.context
    ctx.block_model_df = None
    ctx.mtype_phase_data = None
    ctx.mtype_cog_bins = None
    ctx.mtype_bins_index = None
    ctx.mtype_summary = {}
    ctx.stype_runs = {}
    ctx.export_zip_bytes = None
    ctx.dataset_name = "No Block Model Loaded"
    for k in ctx.node_states:
        if k != "ingestion_config":
            ctx.node_states[k] = "IDLE"
            ctx.node_timings[k] = 0.0
            ctx.node_logs[k] = []
    return get_current_state()

@app.get("/api/export-zip")
def export_zip():
    ctx = ORCHESTRATOR.context
    if not ctx.export_zip_bytes:
        ORCHESTRATOR.run_node("export_bundle")
    if not ctx.export_zip_bytes:
        raise HTTPException(status_code=400, detail="No calculation results available for export.")
    
    return Response(
        content=ctx.export_zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=PhaseFiles_Export.zip"}
    )

# Static Frontend Mount
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        dist_root = os.path.realpath(FRONTEND_DIST)
        clean_path = full_path.lstrip("/\\")
        target_path = os.path.realpath(os.path.join(dist_root, clean_path))
        if (
            target_path == dist_root or target_path.startswith(dist_root + os.sep)
        ) and os.path.isfile(target_path):
            return FileResponse(target_path)
        return FileResponse(os.path.join(dist_root, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=1943, reload=False)
