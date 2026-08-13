from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "apps" / "desktop"


def test_d5_renderer_adds_no_third_party_chart_runtime() -> None:
    package = (DESKTOP / "package.json").read_text(encoding="utf-8")
    package_lower = package.lower()

    assert '"license": "Apache-2.0"' in package
    for runtime_dependency in (
        '"@tauri-apps/api"',
        '"react"',
        '"react-dom"',
    ):
        assert runtime_dependency in package

    workbench = (DESKTOP / "src" / "Workbench.tsx").read_text(encoding="utf-8")
    workbench_lower = workbench.lower()
    for chart_package in (
        "chart.js",
        "highcharts",
        "lightweight-charts",
        "plotly",
        "recharts",
        "d3",
        "echarts",
    ):
        assert chart_package not in package_lower
        assert chart_package not in workbench_lower

    assert "<svg" in workbench
    assert "<polyline" in workbench
    assert "workbench-volume-svg" in workbench
