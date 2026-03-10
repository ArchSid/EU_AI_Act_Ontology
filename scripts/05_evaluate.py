"""
05_evaluate.py — Structural metrics evaluation
================================================
Computes automated structural quality metrics for the ontology.

Input:   ontology/eu-ai-act.ttl
Output:  ontology/evaluation_report.txt  (also printed to console)

Note: Task-based competency question evaluation is done manually
      in Protégé using the queries in sparql/sparql_competency_queries.sparql
"""

from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.term import URIRef, Literal
from collections import Counter, defaultdict
import sys, os

# ─── Setup ──────────────────────────────────────────────────────────────────────
os.makedirs("ontology", exist_ok=True)

class Tee:
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.file = open(filepath, "w")
    def write(self, msg):
        self.terminal.write(msg)
        self.file.write(msg)
    def flush(self):
        self.terminal.flush()
        self.file.flush()
    def close(self):
        self.file.close()

tee = Tee("ontology/evaluation_report.txt")
sys.stdout = tee

EU = Namespace("https://w3id.org/euaiact/ontology#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.parse("ontology/eu-ai-act.ttl", format="turtle")
g.bind("euai", EU)

# ═════════════════════════════════════════════════════════════════════════════════
#  PART A — STRUCTURAL METRICS
# ═════════════════════════════════════════════════════════════════════════════════
print("=" * 72)
print("  PART A: STRUCTURAL METRICS")
print("=" * 72)
print()

# A1. Basic counts
classes = set(g.subjects(RDF.type, OWL.Class))
obj_props = set(g.subjects(RDF.type, OWL.ObjectProperty))
data_props = set(g.subjects(RDF.type, OWL.DatatypeProperty))
individuals = set(g.subjects(RDF.type, OWL.NamedIndividual))
n_triples = len(g)

print("A1. Basic counts")
print(f"    OWL Classes:            {len(classes)}")
print(f"    Object Properties:      {len(obj_props)}")
print(f"    Datatype Properties:    {len(data_props)}")
print(f"    Named Individuals:      {len(individuals)}")
print(f"    Total Triples:          {n_triples}")
print()

# A2. Class hierarchy depth
def compute_depth(cls, parents_map, memo={}):
    if cls in memo:
        return memo[cls]
    parents = parents_map.get(cls, [])
    if not parents:
        memo[cls] = 0
        return 0
    d = 1 + max(compute_depth(p, parents_map, memo) for p in parents)
    memo[cls] = d
    return d

parents_map = defaultdict(list)
for child, parent in g.subject_objects(RDFS.subClassOf):
    if isinstance(parent, URIRef) and parent in classes:
        parents_map[child].append(parent)

depths = {}
for c in classes:
    depths[c] = compute_depth(c, parents_map, {})

max_depth = max(depths.values()) if depths else 0
avg_depth = sum(depths.values()) / len(depths) if depths else 0
root_classes = [c for c in classes if c not in parents_map]

print("A2. Class hierarchy depth")
print(f"    Max depth:              {max_depth}")
print(f"    Average depth:          {avg_depth:.2f}")
print(f"    Root classes (no parent): {len(root_classes)}")
if max_depth > 0:
    deepest = [str(c).replace(str(EU), "euai:") for c, d in depths.items() if d == max_depth]
    print(f"    Deepest class(es):      {', '.join(deepest[:5])}")
print()

# A3. Property-to-class ratio
prop_count = len(obj_props) + len(data_props)
ratio = prop_count / len(classes) if classes else 0
print("A3. Property-to-class ratio")
print(f"    Total properties:       {prop_count}")
print(f"    Classes:                {len(classes)}")
print(f"    Ratio:                  {ratio:.2f}")
print()

# A4. Individual-to-class ratio (population density)
print("A4. Individual-to-class population density")
class_pop = Counter()
for indiv in individuals:
    for t in g.objects(indiv, RDF.type):
        if t in classes:
            class_pop[t] += 1

populated = sum(1 for c in classes if class_pop[c] > 0)
empty_classes = [str(c).replace(str(EU), "euai:") for c in classes if class_pop[c] == 0]
print(f"    Populated classes:      {populated} / {len(classes)}")
print(f"    Empty classes:          {len(empty_classes)}")
if empty_classes:
    print(f"    Empty class names:      {', '.join(sorted(empty_classes))}")
print(f"    Avg individuals/class:  {len(individuals)/len(classes):.1f}")
print()

# A5. Orphan individuals (no incoming/outgoing domain-specific relationships)
print("A5. Orphan individuals (no euai: relationships)")
orphan_count = 0
for indiv in individuals:
    has_rel = False
    # outgoing
    for p, o in g.predicate_objects(indiv):
        if str(p).startswith(str(EU)):
            has_rel = True
            break
    if not has_rel:
        # incoming
        for s, p in g.subject_predicates(indiv):
            if str(p).startswith(str(EU)):
                has_rel = True
                break
    if not has_rel:
        orphan_count += 1

print(f"    Orphan individuals:     {orphan_count} / {len(individuals)}")
print(f"    Connected rate:         {100*(1 - orphan_count/len(individuals)):.1f}%")
print()

# A6. Label & definition coverage
labelled = sum(1 for i in individuals if (i, RDFS.label, None) in g)
defined = sum(1 for i in individuals if (i, SKOS.definition, None) in g)
print("A6. Annotation coverage")
print(f"    Individuals with label:       {labelled} / {len(individuals)} ({100*labelled/len(individuals):.1f}%)")
print(f"    Individuals with definition:  {defined} / {len(individuals)} ({100*defined/len(individuals):.1f}%)")
print()

# A7. Relationship type distribution
print("A7. Relationship type distribution (top 15)")
rel_counts = Counter()
for s, p, o in g:
    if str(p).startswith(str(EU)) and isinstance(s, URIRef) and isinstance(o, URIRef):
        rel_counts[str(p).replace(str(EU), "")] += 1
for rel, cnt in rel_counts.most_common(15):
    print(f"    {rel:40s} {cnt:>5}")
print(f"    {'--- total ---':40s} {sum(rel_counts.values()):>5}")
print()

# A8. Entity type distribution
print("A8. Entity type distribution")
type_counts = Counter()
for indiv in individuals:
    for t in g.objects(indiv, RDF.type):
        if t in classes:
            type_counts[str(t).replace(str(EU), "")] += 1
for t_name, cnt in type_counts.most_common():
    print(f"    {t_name:40s} {cnt:>5}")
print()

# ─── Summary ────────────────────────────────────────────────────────────────────
print("=" * 72)
print("  SUMMARY")
print("=" * 72)
print()
print(f"  Classes: {len(classes)}, Properties: {prop_count}, Individuals: {len(individuals)}")
print(f"  Max class depth: {max_depth}, Avg depth: {avg_depth:.2f}")
print(f"  Property/class ratio: {ratio:.2f}")
print(f"  Orphan individuals: {orphan_count}/{len(individuals)} ({100*orphan_count/len(individuals):.1f}%)")
print(f"  Label coverage: {100*labelled/len(individuals):.1f}%, Definition coverage: {100*defined/len(individuals):.1f}%")
print()
print("  Note: For task-based competency question evaluation, run the queries")
print("  in sparql/sparql_competency_queries.sparql manually in Protégé.")
print()

sys.stdout = tee.terminal
tee.close()
print(f"Report saved to: ontology/evaluation_report.txt")
