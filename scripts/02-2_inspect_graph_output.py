"""
02-2_inspect_graph_output.py
Inspect GraphRAG parquet outputs and export them as readable CSV files.

Outputs (written to graphrag/output/csv/):
  summary.csv              – one-row-per-file overview of all parquet outputs
  entities.csv             – all extracted entities (title, type, description, …)
  relationships.csv        – all extracted relationships (source → target)
  communities.csv          – Leiden community membership
  community_reports.csv    – LLM-generated community summaries
  text_units.csv           – text chunks with linked entity / relationship IDs
  documents.csv            – source document metadata
"""

import pandas as pd
from glob import glob
from pathlib import Path

OUTPUT_DIR = Path("graphrag/output")
CSV_DIR = OUTPUT_DIR / "csv"
CSV_DIR.mkdir(exist_ok=True)

# ── 1. Read every parquet file ──────────────────────────────────────────
frames: dict[str, pd.DataFrame] = {}
summary_rows: list[dict] = []

for filepath in sorted(OUTPUT_DIR.glob("*.parquet")):
    name = filepath.stem
    df = pd.read_parquet(filepath)
    frames[name] = df
    summary_rows.append(
        {
            "file": f"{name}.parquet",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": ", ".join(df.columns.tolist()),
        }
    )

# ── 2. Summary table ───────────────────────────────────────────────────
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(CSV_DIR / "summary.csv", index=False)
print("=" * 70)
print("  GRAPHRAG OUTPUT SUMMARY")
print("=" * 70)
print(summary_df.to_string(index=False))
print()

# ── 3. Export each file with human-readable columns ─────────────────────

# --- Entities ---
if "entities" in frames:
    ent = frames["entities"][
        ["human_readable_id", "title", "type", "description", "frequency", "degree"]
    ].copy()
    ent.columns = ["id", "entity_name", "entity_type", "description", "frequency", "degree"]
    ent = ent.sort_values("degree", ascending=False).reset_index(drop=True)
    ent.to_csv(CSV_DIR / "entities.csv", index=False)
    print(f"  entities.csv          – {len(ent)} rows exported")

# --- Relationships ---
if "relationships" in frames:
    rel = frames["relationships"][
        ["human_readable_id", "source", "target", "description", "weight", "combined_degree"]
    ].copy()
    rel.columns = ["id", "source", "target", "description", "weight", "combined_degree"]
    rel = rel.sort_values("weight", ascending=False).reset_index(drop=True)
    rel.to_csv(CSV_DIR / "relationships.csv", index=False)
    print(f"  relationships.csv     – {len(rel)} rows exported")

# --- Communities ---
if "communities" in frames:
    comm = frames["communities"][
        ["human_readable_id", "community", "level", "title", "size"]
    ].copy()
    comm.columns = ["id", "community", "level", "title", "size"]
    comm = comm.sort_values(["level", "community"]).reset_index(drop=True)
    comm.to_csv(CSV_DIR / "communities.csv", index=False)
    print(f"  communities.csv       – {len(comm)} rows exported")

# --- Community reports ---
if "community_reports" in frames:
    cr = frames["community_reports"][
        ["human_readable_id", "community", "level", "title", "summary", "rank", "size"]
    ].copy()
    cr.columns = ["id", "community", "level", "title", "summary", "rank", "size"]
    cr = cr.sort_values("rank", ascending=False).reset_index(drop=True)
    cr.to_csv(CSV_DIR / "community_reports.csv", index=False)
    print(f"  community_reports.csv – {len(cr)} rows exported")

# --- Text units ---
if "text_units" in frames:
    tu = frames["text_units"][
        ["human_readable_id", "n_tokens"]
    ].copy()
    # count linked entities and relationships per chunk
    tu_raw = frames["text_units"]
    tu["linked_entities"] = tu_raw["entity_ids"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    tu["linked_relationships"] = tu_raw["relationship_ids"].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    tu["text_preview"] = tu_raw["text"].str[:300]
    tu.columns = ["chunk_id", "n_tokens", "linked_entities", "linked_relationships", "text_preview"]
    tu.to_csv(CSV_DIR / "text_units.csv", index=False)
    print(f"  text_units.csv        – {len(tu)} rows exported")

# --- Documents ---
if "documents" in frames:
    doc = frames["documents"].copy()
    # keep only metadata columns (drop the raw text which is huge)
    keep = [c for c in doc.columns if c != "raw_content"]
    if "raw_content" in doc.columns:
        doc["text_length"] = doc["raw_content"].str.len()
    doc[keep + (["text_length"] if "text_length" in doc.columns else [])].to_csv(
        CSV_DIR / "documents.csv", index=False
    )
    print(f"  documents.csv         – {len(doc)} rows exported")

print(f"\nAll CSV files written to: {CSV_DIR}/")

# ── 4. Print key statistics ────────────────────────────────────────────
print("\n" + "=" * 70)
print("  KEY STATISTICS")
print("=" * 70)
if "entities" in frames:
    e = frames["entities"]
    print(f"  Total entities       : {len(e)}")
    print(f"  Entity types         : {e['type'].nunique()}  {sorted(e['type'].unique().tolist())}")
    print(f"  Highest-degree entity: {e.loc[e['degree'].idxmax(), 'title']}  (degree {e['degree'].max()})")
if "relationships" in frames:
    r = frames["relationships"]
    print(f"  Total relationships  : {len(r)}")
    print(f"  Max edge weight      : {r['weight'].max()}")
if "communities" in frames:
    c = frames["communities"]
    print(f"  Total communities    : {len(c)}")
    print(f"  Hierarchy levels     : {sorted(c['level'].unique().tolist())}")
    print(f"  Largest community    : {c.loc[c['size'].idxmax(), 'title']}  ({c['size'].max()} entities)")
if "text_units" in frames:
    print(f"  Text chunks          : {len(frames['text_units'])}")
print()
