# EU AI Act Ontology

An OWL 2 ontology of the [EU Artificial Intelligence Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) (Regulation 2024/1689), built using an LLM-powered knowledge-graph extraction pipeline.

## Highlights

| Metric | Value |
|--------|-------|
| Classes | 37 |
| Named individuals | 1,453 |
| Relationships | 2,473 |
| Total triples | 8,620 |
| SHACL validation | Conforms ✅ |
| HermiT reasoner | Consistent ✅ |

## What It Covers

- **AI systems** across the full risk spectrum — prohibited practices, high-risk systems, general-purpose AI models, and systemic-risk models
- **Supply-chain actors** — providers, deployers, importers, distributors, authorised representatives
- **Oversight bodies** — AI Office, European AI Board, national competent authorities, notified bodies
- **Obligations & requirements** — conformity assessment, transparency, post-market monitoring, risk management, data governance, human oversight, robustness, technical documentation
- **Risk classification** — the four-tier risk framework, Annex III categories, exclusion conditions, delegated acts

## How It Was Built

The ontology is constructed through a five-stage automated pipeline:

```
EUR-Lex ──► Scrape ──► GraphRAG + Gemini ──► OWL Ontology ──► SHACL Validation ──► Reasoner Check
             (1)           (2)                   (3)              (4)                  (5)
```

1. **Scrape** — Download the full Act text from EUR-Lex (`01_scrape_act.py`)
2. **Extract** — Run [Microsoft GraphRAG](https://github.com/microsoft/graphrag) v3.0.5 with Google Gemini to extract 1,444 entities and 2,473 relationships from the text (`02_run_graphrag.py`)
3. **Build ontology** — Merge a manually curated class hierarchy (37 classes, 22 subclass axioms) with GraphRAG-extracted entities and relationships (`03_graph_to_owl.py`)
4. **Validate** — Run SHACL shape validation to check constraints (`04_validate.py`)
5. **Reasoner check** — Load in Protégé 5.6 and run HermiT to verify logical consistency

## Quick Start

### Prerequisites

- Python 3.12+
- A Google Gemini API key (set as `GRAPHRAG_API_KEY` environment variable)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/EU_AI_act_GraphRAG.git
cd EU_AI_act_GraphRAG

# Install dependencies
pip install graphrag rdflib pyshacl pandas networkx matplotlib pyvis
```

### Run the Pipeline

```bash
# 1. Scrape the EU AI Act text
python scripts/01_scrape_act.py

# 2. Run GraphRAG extraction
python scripts/02_run_graphrag.py

# 2b. (Optional) Export GraphRAG outputs to CSV for inspection
python scripts/02-2_inspect_graph_output.py

# 3. Build the OWL ontology
python scripts/03_graph_to_owl.py

# 4. Validate with SHACL
python scripts/04_validate.py

# 5. Run structural evaluation metrics
python scripts/05_evaluate.py
```

> **Note:** Step 5 (HermiT reasoner check) is performed manually in [Protégé](https://protege.stanford.edu/) by loading `ontology/eu-ai-act.owl` and running *Reasoner → HermiT → Start Reasoner*.

### Query the Ontology

Five SPARQL competency queries are provided in `sparql/sparql_competency_queries.sparql`. Open the ontology in Protégé and run them via *Window → Tabs → SPARQL Query*.

Example — find all prohibited AI practices:
```sparql
SELECT ?s ?label
WHERE {
    ?s rdf:type euai:ProhibitedAIPractice ;
       rdfs:label ?label .
}
```

## Project Structure

```
EU_AI_act_GraphRAG/
├── data/input/              # Source text of the EU AI Act
├── docs/
│   ├── documentation.md     # Full documentation note
│   ├── validation_results.md
│   └── evaluation_structural_metrics.md
├── graphrag/
│   ├── settings.yml         # GraphRAG configuration
│   ├── prompts/             # Custom entity extraction prompt
│   └── output/              # GraphRAG outputs (parquet + CSV)
├── ontology/
│   ├── eu-ai-act.owl        # Ontology (RDF/XML)
│   ├── eu-ai-act.ttl        # Ontology (Turtle)
│   ├── kg_interactive.html  # Interactive KG visualisation
│   ├── validation_report.txt
│   └── evaluation_report.txt
├── scripts/                 # Pipeline scripts (stages 1–5)
├── sparql/                  # SPARQL competency queries
└── lib/                     # JS/CSS for interactive visualisation
```

## Ontology Namespace

```
https://w3id.org/euaiact/ontology#
```

Prefix: `euai:`

Standard vocabularies reused: `rdfs:label`, `skos:definition`, `dcterms:description`, `dcterms:source`.

## Key Design Decisions

- **GraphRAG over direct prompting** — Chunked extraction + cross-chunk deduplication gives far more systematic coverage of a 113-article legal text than single-prompt approaches
- **Hybrid construction** — A manually curated class hierarchy provides structure; GraphRAG-extracted entities populate it with instances
- **All entities kept** — Every entity extracted by GraphRAG is included; filtering is controlled upstream by the 15 entity types in the extraction prompt
- **Relationship heuristic** — Free-text relationship descriptions are matched against 27 known property names; unmatched ones default to `euai:relatedTo`

## Tech Stack

| Component | Technology |
|-----------|------------|
| Graph extraction | [Microsoft GraphRAG](https://github.com/microsoft/graphrag) v3.0.5 |
| LLM | Google Gemini (`gemini-3.1-flash-lite-preview`) |
| Embeddings | Google Gemini (`gemini-embedding-001`) |
| Ontology library | [rdflib](https://rdflib.readthedocs.io/) |
| SHACL validation | [pyshacl](https://github.com/RDFLib/pySHACL) |
| Reasoner | HermiT (via [Protégé](https://protege.stanford.edu/) 5.6) |
| Visualisation | [pyvis](https://pyvis.readthedocs.io/), matplotlib, networkx |

## Documentation

For full details on methodology, modelling decisions, validation, and evaluation, see [docs/documentation.md](docs/documentation.md).

## License

This project is for academic/research purposes. The EU AI Act text is sourced from [EUR-Lex](https://eur-lex.europa.eu/) and is available under the [European Union Public Licence](https://eur-lex.europa.eu/content/legal-notice/legal-notice.html).