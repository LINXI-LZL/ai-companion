import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "data" / "public_sources" / "data_sources.json"


def load_source_status(path=SOURCE_FILE):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    sources = []
    for source in payload.get("sources", []):
        sources.append(
            {
                "id": source["id"],
                "name": source["name"],
                "type": source["type"],
                "license": source["license"],
                "download_policy": source["download_policy"],
                "traffic_level": source["traffic_level"],
                "fit_for_product": source["fit_for_product"],
                "status": source["status"],
                "recommended_use": source.get("recommended_use", []),
                "risks": source.get("risks", []),
                "url": source["url"],
            }
        )
    return sources
