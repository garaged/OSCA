from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "apps" / "desktop"


def test_d5_renderer_adds_no_third_party_chart_runtime() -> None:
    package = json.loads((DESKTOP / "package.json").read_text(encoding="utf-8"))
    dependencies = set(package["dependencies"])

    assert dependencies == {"@tauri-apps/api", "react", "react-dom"}
    assert package["license"] == "Apache-2.0"

    workbench = (DESKTOP / "src" / "Workbench.tsx").read_text(encoding="utf-8")
    for chart_package in (
        "chart.js",
        "highcharts",
        "lightweight-charts",
        "plotly",
        "recharts",
        "d3",
        "echarts",
    ):
        assert chart_package not in workbench.lower()

    assert "<svg" in workbench
    assert "<polyline" in workbench
    assert "workbench-volume-svg" in workbench
