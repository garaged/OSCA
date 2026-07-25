from pathlib import Path
from uuid import UUID, uuid4

from osca.intelligence import (
    AnalysisPackFamily,
    AnalysisPackManifest,
    AnalyticalResultBundle,
    EvidenceKind,
    EvidenceReference,
    MethodologyDisclosure,
    PackDataRequirement,
    SQLiteIntelligenceStore,
    VisualizationPackSpec,
)


def build_manifest() -> AnalysisPackManifest:
    return AnalysisPackManifest(
        pack_id="fundamental-core",
        pack_version="1.0.0",
        pack_family=AnalysisPackFamily.FUNDAMENTAL_VALUATION,
        supported_asset_classes=("equity",),
        output_kinds=(EvidenceKind.FINDING,),
        data_requirements=(
            PackDataRequirement(
                capability="financial-statements",
                interval="quarterly",
                quality_policy_id="strict",
            ),
        ),
        methodology=MethodologyDisclosure(
            methodology_id="dcf-screen",
            methodology_version="1.0.0",
            assumptions=("discount-rate-declared",),
            limitations=("not-investment-advice",),
            documentation_uri="docs/intelligence/dcf-screen.md",
        ),
    )


def build_result(project_id: UUID, pack_id: str = "fundamental-core") -> AnalyticalResultBundle:
    evidence = EvidenceReference(
        evidence_id=uuid4(),
        evidence_kind=EvidenceKind.OBSERVATION,
        source_pack_id=pack_id,
        dataset_revision_ids=(uuid4(),),
        methodology_id="dcf-screen",
        confidence=0.8,
    )
    return AnalyticalResultBundle(
        project_id=project_id,
        pack_id=pack_id,
        pack_version="1.0.0",
        result_kind=EvidenceKind.FINDING,
        evidence=(evidence,),
    )


def test_intelligence_store_round_trips_pack_manifest(tmp_path: Path) -> None:
    store = SQLiteIntelligenceStore(tmp_path / "intelligence.sqlite")
    store.initialize()
    manifest = build_manifest()

    store.save_pack_manifest(manifest)

    assert store.list_pack_manifests() == (manifest,)


def test_intelligence_store_queries_project_results(tmp_path: Path) -> None:
    store = SQLiteIntelligenceStore(tmp_path / "intelligence.sqlite")
    store.initialize()
    project_id = uuid4()
    first = build_result(project_id)
    second = build_result(uuid4())

    store.save_result_bundle(first)
    store.save_result_bundle(second)

    assert store.list_result_bundles(str(project_id)) == (first,)


def test_intelligence_store_queries_paper_scenarios(tmp_path: Path) -> None:
    from osca.intelligence import PortfolioScenarioReport

    store = SQLiteIntelligenceStore(tmp_path / "intelligence.sqlite")
    store.initialize()
    paper_account_id = uuid4()
    scenario = PortfolioScenarioReport(
        paper_account_id=paper_account_id,
        scenario_id="rates-up",
        base_currency="USD",
        exposure_metric_ids=("gross-exposure",),
        stress_assumption_ids=("rates-up",),
    )

    store.save_portfolio_scenario(scenario)

    assert store.list_portfolio_scenarios(str(paper_account_id)) == (scenario,)


def test_intelligence_store_persists_visualization_pack_spec(tmp_path: Path) -> None:
    store = SQLiteIntelligenceStore(tmp_path / "intelligence.sqlite")
    store.initialize()
    spec = VisualizationPackSpec(
        pack_id="chart-pack",
        supported_result_kinds=(EvidenceKind.FINDING,),
    )

    store.save_visualization_pack_spec(spec)
    manifests = store.list_pack_manifests()

    assert manifests == ()
