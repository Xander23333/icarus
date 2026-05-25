#!/usr/bin/env python3
"""
NTP daily arxiv harvester.

Deterministic pre-fetch step run before the agent's reasoning step.
- Scans 8 NTP-relevant arxiv category × keyword query strategies
- Dedups against state/read_ids.json
- Writes state/harvest_<UTC_DATE>.json with raw candidates
- Stays well under arxiv rate limit (sleep 5s between queries, -m 60 timeout)

Output JSON schema:
{
  "harvested_utc": "2026-05-26T12:34:56Z",
  "queries_run": [...],
  "raw_count": int,
  "deduped_count": int,
  "candidates": [
    {"id": "2405.12345", "title": "...", "authors": "...", "primary_cat": "...",
     "cats": [...], "published": "YYYY-MM-DD", "updated": "YYYY-MM-DD",
     "abstract": "...", "pdf": "https://arxiv.org/pdf/2405.12345",
     "matched_queries": ["formal_limits", "reasoning"]}
  ]
}

No deps beyond stdlib.
"""
import json, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent  # ntp/
STATE = ROOT / "state"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

# 8-topic query strategy. Each entry: (topic_tag, search_query).
# Use OR within abs:(...) to widen recall; rely on agent for precision filter.
QUERIES = [
    ("formal_limits",
     'abs:("transformer expressivity" OR "transformer expressiveness" OR "circuit complexity" OR "TC0" OR "computational power of transformers" OR "next-token prediction" OR "autoregressive limits")'),
    ("reasoning",
     'abs:("chain of thought faithfulness" OR "CoT faithfulness" OR "reasoning faithfulness" OR "compositional generalization" OR "systematic generalization" OR "pattern matching vs reasoning")'),
    ("grounding",
     'abs:("symbol grounding" OR "grounded language learning" OR "multimodal grounding" OR "semantic grounding" OR "world grounding")'),
    ("causality",
     'abs:("causal reasoning" OR "counterfactual reasoning" OR "causal inference" OR "Pearl causal hierarchy" OR "interventional reasoning") AND (abs:LLM OR abs:"language model" OR abs:transformer)'),
    ("embodiment",
     'abs:("embodied AI" OR "embodied agent" OR "robotics foundation model" OR "vision language action" OR "VLA" OR "active perception")'),
    ("online_learning",
     'abs:("continual learning" OR "lifelong learning" OR "catastrophic forgetting" OR "online adaptation" OR "non-stationary") AND (abs:LLM OR abs:"language model" OR abs:foundation)'),
    ("world_model",
     'abs:("world model" OR "latent dynamics" OR "model-based reinforcement learning" OR "video world model" OR "JEPA" OR "Dreamer")'),
    ("scaling_limits",
     'abs:("scaling law" OR "in-context learning theory" OR "sample complexity" OR "data efficiency") AND (abs:LLM OR abs:"language model" OR abs:transformer)'),
]

# Cap per query — agent will further filter
MAX_RESULTS = 25

def fetch(query: str) -> bytes:
    url = ("https://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({
               "search_query": query,
               "sortBy": "submittedDate",
               "sortOrder": "descending",
               "max_results": MAX_RESULTS,
           }))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NTPResearchBot/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if len(data) < 1000:
        # rate-limited or empty
        raise RuntimeError(f"arxiv response too small ({len(data)} bytes), likely 429")
    return data

def parse(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    out = []
    for e in root.findall("a:entry", NS):
        arxiv_id = e.find("a:id", NS).text.strip().split("/abs/")[-1]
        # strip version suffix for dedup key but keep full id for citation
        base_id = arxiv_id.split("v")[0]
        title = " ".join(e.find("a:title", NS).text.split())
        authors = ", ".join(a.find("a:name", NS).text for a in e.findall("a:author", NS))
        pub = e.find("a:published", NS).text[:10]
        upd = e.find("a:updated", NS).text[:10]
        abstract = " ".join(e.find("a:summary", NS).text.split())
        prim = e.find("arxiv:primary_category", NS)
        primary_cat = prim.get("term") if prim is not None else ""
        cats = [c.get("term") for c in e.findall("a:category", NS)]
        out.append({
            "id": base_id,
            "id_versioned": arxiv_id,
            "title": title,
            "authors": authors,
            "primary_cat": primary_cat,
            "cats": cats,
            "published": pub,
            "updated": upd,
            "abstract": abstract,
            "pdf": f"https://arxiv.org/pdf/{base_id}",
        })
    return out

def main():
    read_ids_path = STATE / "read_ids.json"
    read_ids = set(json.loads(read_ids_path.read_text()).get("ids", []))

    seen = {}  # id -> candidate (merges matched_queries)
    queries_run = []
    raw_count = 0
    errors = []

    for tag, q in QUERIES:
        try:
            xml = fetch(q)
            entries = parse(xml)
            raw_count += len(entries)
            for ent in entries:
                if ent["id"] in read_ids:
                    continue
                if ent["id"] in seen:
                    seen[ent["id"]]["matched_queries"].append(tag)
                else:
                    ent["matched_queries"] = [tag]
                    seen[ent["id"]] = ent
            queries_run.append({"tag": tag, "query": q, "hits": len(entries), "status": "ok"})
        except Exception as e:
            errors.append({"tag": tag, "error": str(e)})
            queries_run.append({"tag": tag, "query": q, "hits": 0, "status": f"error: {e}"})
        time.sleep(5)

    candidates = sorted(seen.values(), key=lambda x: x["published"], reverse=True)

    out = {
        "harvested_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "queries_run": queries_run,
        "errors": errors,
        "raw_count": raw_count,
        "deduped_count": len(candidates),
        "candidates": candidates,
    }
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outpath = STATE / f"harvest_{today}.json"
    outpath.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    # Also write a "latest" symlink-style file
    (STATE / "harvest_latest.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    # Compact stdout summary for the cron agent
    print(f"HARVEST_OK date={today} raw={raw_count} deduped={len(candidates)} errors={len(errors)} -> {outpath}")
    if errors:
        print("ERRORS:", json.dumps(errors)[:500])

if __name__ == "__main__":
    main()
