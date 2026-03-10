from rdflib import Graph
from pyshacl import validate
import sys
import os

os.makedirs("ontology", exist_ok=True)

# Tee output to both console and file
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

tee = Tee("ontology/validation_report.txt")
sys.stdout = tee

data_graph = Graph()
data_graph.parse("ontology/eu-ai-act.ttl", format="turtle")

# Basic shape: every HighRiskAISystem should have an articleReference
SHACL_SHAPES = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix euai: <https://w3id.org/euaiact/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

euai:HighRiskAISystemShape
    a sh:NodeShape ;
    sh:targetClass euai:HighRiskAISystem ;
    sh:property [
        sh:path euai:articleReference ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "HighRiskAISystem must have an article reference."
    ] .

euai:ObligationShape
    a sh:NodeShape ;
    sh:targetClass euai:Obligation ;
    sh:property [
        sh:path <http://www.w3.org/2000/01/rdf-schema#label> ;
        sh:minCount 1 ;
        sh:message "Every Obligation must have a label."
    ] .
"""

shapes_graph = Graph()
shapes_graph.parse(data=SHACL_SHAPES, format="turtle")

conforms, results_graph, results_text = validate(
    data_graph, shacl_graph=shapes_graph, inference='rdfs', debug=False
)
print(f"Conforms: {conforms}")
print(results_text)

# Basic metrics
print("\n=== ONTOLOGY METRICS ===")
from rdflib import OWL, RDF
n_classes = len(list(data_graph.subjects(RDF.type, OWL.Class)))
n_obj_props = len(list(data_graph.subjects(RDF.type, OWL.ObjectProperty)))
n_individuals = len(list(data_graph.subjects(RDF.type, OWL.NamedIndividual)))
n_triples = len(data_graph)
print(f"Classes: {n_classes}")
print(f"Object Properties: {n_obj_props}")
print(f"Named Individuals: {n_individuals}")
print(f"Total Triples: {n_triples}")

sys.stdout = tee.terminal
tee.close()
print(f"\nReport saved to: ontology/validation_report.txt")