import subprocess
import time
import sys
from pathlib import Path

def validate_environment():
    """Validate all required files exist before running GraphRAG."""

    required_files = {
        "GraphRAG config":          Path("graphrag/settings.yml"),
        "Entity extraction prompt": Path("graphrag/prompts/2-entity_extraction.txt"),
        "Input data directory":     Path("data/input"),
    }

    print("🔍 Pre-flight checks...")
    all_ok = True

    for name, path in required_files.items():
        if path.exists():
            if path.is_file():
                size_kb = path.stat().st_size / 1024
                print(f"   ✅ {name}: {path} ({size_kb:.1f} KB)")
            else:
                # It is a directory — count .txt files inside
                files = list(path.glob("*.txt"))
                print(f"   ✅ {name}: {path} ({len(files)} .txt file(s) found)")
                if len(files) == 0:
                    print(f"   ⚠️  WARNING: No .txt files found in {path}")
                    print(f"        Run: python scripts/01_scrape_act.py")
        else:
            print(f"   ❌ MISSING: {name} not found at {path}")
            all_ok = False

    # Extra check — warn if old prompt filename still being used
    old_prompt = Path("graphrag/prompts/entity_extraction.txt")
    new_prompt = Path("graphrag/prompts/2-entity_extraction.txt")
    if old_prompt.exists() and not new_prompt.exists():
        print(f"\n   ⚠️  WARNING: Found old prompt '{old_prompt}'")
        print(f"        but new prompt '{new_prompt}' is missing.")
        print(f"        Save your V10 prompt as: graphrag/prompts/2-entity_extraction.txt")
        all_ok = False

    if not all_ok:
        print("\n❌ Pre-flight checks failed. Fix the above before running.")
        sys.exit(1)

    print("✅ All pre-flight checks passed.\n")


def run_graphrag_with_retry(max_attempts=3):
    """Run GraphRAG indexing with automatic retry on rate limit errors."""

    validate_environment()

    for attempt in range(1, max_attempts + 1):
        print(f"\n🚀 GraphRAG indexing attempt {attempt}/{max_attempts}")

        result = subprocess.run(
            ["graphrag", "index", "--root", "./graphrag"],
            capture_output=False,   # Show live output in terminal
            text=True
        )

        if result.returncode == 0:
            print("✅ GraphRAG indexing complete!")
            _report_output_summary()
            return True

        if attempt < max_attempts:
            wait_time = 60 * attempt   # 60s after attempt 1, 120s after attempt 2
            print(f"⚠️  Pipeline failed. Waiting {wait_time}s before retry...")
            print("   (Cache is preserved — will resume from last checkpoint)")
            time.sleep(wait_time)
        else:
            print("❌ All attempts failed.")
            print("   Check graphrag/logs/indexing-engine.log for details.")
            sys.exit(1)


def _report_output_summary():
    """After a successful run, report what parquet files were produced."""
    output_dir = Path("graphrag/output")

    if not output_dir.exists():
        print("⚠️  graphrag/output/ not found after run.")
        return

    print("\n📊 Output summary:")

    # GraphRAG 3.x writes into timestamped subdirectories
    # rglob finds parquet files anywhere under graphrag/output/
    parquet_files = list(output_dir.rglob("*.parquet"))

    if not parquet_files:
        print("   ⚠️  No parquet files found in graphrag/output/")
        print("        GraphRAG may have failed silently.")
        print("        Check: graphrag/logs/indexing-engine.log")
        return

    # Key files needed by 03_build_ontology.py
    key_files = {
        "create_final_entities.parquet":      "Entities extracted",
        "create_final_relationships.parquet": "Relationships extracted",
        "create_final_communities.parquet":   "Communities detected",
        "create_final_text_units.parquet":    "Text units processed",
    }

    for filename, label in key_files.items():
        matches = [f for f in parquet_files if f.name == filename]
        if matches:
            size_kb = matches[0].stat().st_size / 1024
            print(f"   ✅ {label}: {filename} ({size_kb:.1f} KB)")
        else:
            print(f"   ⚠️  Not found: {filename}")

    print(f"\n   📁 Output location: {output_dir.resolve()}")
    print("   ➡️  Next step: run python scripts/03_build_ontology.py")


if __name__ == "__main__":
    run_graphrag_with_retry()