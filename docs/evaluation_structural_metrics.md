# Evaluation A — Structural Metrics

## Overview

This evaluation measures the ontology's internal structure using eight automated metrics. No manual annotation or gold standard is required — the script analyses the serialised ontology file directly.

**Script:** `scripts/05_evaluate.py`
**Input:** `ontology/eu-ai-act.ttl`
**Output:** Console report + `ontology/evaluation_report.txt`

## Method

The evaluation script loads the Turtle file into an `rdflib.Graph` and computes the following metrics:

### A1. Basic Counts

Counts the number of OWL classes (`owl:Class`), object properties (`owl:ObjectProperty`), datatype properties (`owl:DatatypeProperty`), named individuals (`owl:NamedIndividual`), and total triples in the graph. These provide a high-level picture of ontology size and complexity.

### A2. Class Hierarchy Depth

For each class in the ontology namespace, the script recursively follows `rdfs:subClassOf` links upward to compute its depth (number of ancestor levels). The maximum and average depths across all classes are reported, along with the root classes (those with no superclass) and the deepest class path.

### A3. Property-to-Class Ratio

The total number of properties (object + datatype) divided by the number of classes. A ratio close to 1.0 suggests each class has approximately one distinguishing property. Very low ratios may indicate under-specified classes; very high ratios may indicate overly property-heavy modelling.

### A4. Individual-to-Class Population Density

For each class, the script counts how many named individuals are typed to it (`rdf:type`). Classes with zero individuals are listed as "empty" — these are typically backbone classes defined in the curated schema that serve as superclasses (e.g., `Provider ⊑ Actor`), where GraphRAG typed instances to the parent class rather than the subclass.

### A5. Orphan Individuals

An individual is considered an "orphan" if it does not participate in any triple whose predicate is in the ontology namespace (`euai:`), excluding `rdf:type`. Orphans are entities that were extracted but have no domain-specific relationship connecting them to the rest of the graph. A low orphan rate indicates a well-connected knowledge graph.

### A6. Annotation Coverage

Checks what percentage of named individuals have:
- an `rdfs:label` (display name)
- a `skos:definition` (concept definition)

100% coverage is expected due to the post-processing step in `03_graph_to_owl.py` that auto-generates labels from URI fragments for any entity lacking one, and GraphRAG's entity descriptions being mapped to `skos:definition`.

### A7. Relationship Type Distribution

Counts the frequency of each object property used across all triples in the ontology namespace and lists the top 15. This reveals which properties dominate (e.g., `relatedTo` as the catch-all) and which domain-specific properties (e.g., `hasObligation`, `definedInArticle`) have meaningful usage.

### A8. Entity Type Distribution

Groups named individuals by their `rdf:type` class and counts how many individuals belong to each entity type. This shows the distribution of extracted entities across the 15+ types defined in the extraction prompt.

## Results - exported into `docs/evaluation_report.txt`

## How to Reproduce

```bash
cd /path/to/EU_AI_act_GraphRAG
python scripts/05_evaluate.py
```

The script reads `ontology/eu-ai-act.ttl` and writes the report to both the console and `ontology/evaluation_report.txt`.
