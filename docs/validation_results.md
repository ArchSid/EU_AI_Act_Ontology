# Validation Results

## Overview

Validation checks whether the ontology is **correct** — i.e., it conforms to its own constraints and is logically consistent. This is distinct from evaluation (see `docs/evaluation_structural_metrics.md`), which measures ontology **quality** through structural metrics and competency questions.

Two validation checks are applied:
(1) **SHACL shape validation** checks domain-specific constraints programmatically;
(2) **Reasoner consistency checking** verifies logical coherence in Protégé.

**Script:** `scripts/04_validate.py` (SHACL validation only)
**Manual step:** Protégé 5.6 + HermiT reasoner (consistency check)
**Input:** `ontology/eu-ai-act.ttl` (script), `ontology/eu-ai-act.owl` (Protégé)
**Output:** Console report + `ontology/validation_report.txt`

## Method

### Stage 1 — SHACL Shape Validation

The script loads the Turtle ontology into an `rdflib.Graph` and validates it against two SHACL shapes using `pyshacl` with RDFS inference enabled. These two shapes were chosen because they target the highest-impact data quality risks in this pipeline: (1) missing legal provenance on the most consequential entity type, and (2) missing labels on entities created indirectly through RDFS inference rather than direct GraphRAG extraction.

**Shape 1 — HighRiskAISystemShape**
Every individual typed as `euai:HighRiskAISystem` must have at least one `euai:articleReference` (datatype `xsd:string`). This ensures high-risk system entries are traceable to their legal source in the Regulation.

```turtle
euai:HighRiskAISystemShape
    a sh:NodeShape ;
    sh:targetClass euai:HighRiskAISystem ;
    sh:property [
        sh:path euai:articleReference ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "HighRiskAISystem must have an article reference."
    ] .
```

**Shape 2 — ObligationShape**
Every individual typed as `euai:Obligation` must have at least one `rdfs:label`. Since GraphRAG may produce relationship targets that were never extracted as standalone entities (and thus lack labels), a post-processing step in `03_graph_to_owl.py` auto-generates `rdfs:label` annotations from URI fragments for any entity in the ontology namespace that lacks one.

```turtle
euai:ObligationShape
    a sh:NodeShape ;
    sh:targetClass euai:Obligation ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:message "Every Obligation must have a label."
    ] .
```

**RDFS inference.** Validation is run with `inference='rdfs'`, which means individuals that become `Obligation`-typed through `rdfs:range` inference (e.g., targets of `euai:hasObligation` where the property's range is `euai:Obligation`) are also checked against the ObligationShape. This was critical — without RDFS inference, 7 such individuals would have been missed.

### Stage 2 — Reasoner Consistency Check (manual)

This step is performed **manually** and is not part of the `04_validate.py` script. The OWL file (`ontology/eu-ai-act.owl`) is loaded in **Protégé 5.6** and the **HermiT** reasoner is run via *Reasoner → HermiT → Start Reasoner*. This checks for logical contradictions such as unsatisfiable classes, disjointness violations, or inconsistent individual assertions. The ontology is reported as **Consistent**.

## Results

The validation script also prints basic counts as summary context (these are not a validation check — see `docs/evaluation_structural_metrics.md` for the full structural evaluation):

Metrics & Values 
OWL Classes - 37 
Object Properties - 29 
Named Individuals - 1,453 
Total Triples - 8,620 


### SHACL Output
Conforms: True
Validation Report
Conforms: True


Zero violations across both shapes. All 8 `HighRiskAISystem` individuals have article references, and all 301+ `Obligation` individuals (including those inferred via `rdfs:range`) have labels.

### Post-Processing Label Fix

The zero-violation result depends on the post-processing step in `03_graph_to_owl.py`. Before this step was added, 35 URIs lacked `rdfs:label` annotations — 28 as triple subjects and 7 as triple objects that became `Obligation`-typed through RDFS inference. The post-processing scans both `g.subjects()` and `g.objects()` for any URI in the `euai:` namespace without a label and generates one from the URI fragment (e.g., `euai:RISK_MANAGEMENT` → `"Risk Management"`). In total, 68 URIs were auto-labelled.

## How to Reproduce

```bash
cd /path/to/EU_AI_act_GraphRAG
python scripts/04_validate.py
```

The script writes results to both the console and `ontology/validation_report.txt`.

For the reasoner check, open `ontology/eu-ai-act.owl` in Protégé 5.6 and run *Reasoner → HermiT → Start Reasoner*.
