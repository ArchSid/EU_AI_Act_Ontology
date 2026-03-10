import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal, OWL, RDF, RDFS, XSD
from rdflib.namespace import SKOS, DCTERMS
import re

# ─── Namespaces ────────────────────────────────────────────────────────────────
EU_AI = Namespace("https://w3id.org/euaiact/ontology#")
g = Graph()
g.bind("euai", EU_AI)
g.bind("owl", OWL)
g.bind("skos", SKOS)
g.bind("dcterms", DCTERMS)

# ─── Ontology Header ───────────────────────────────────────────────────────────
ONTO_URI = URIRef("https://w3id.org/euaiact/ontology")
g.add((ONTO_URI, RDF.type, OWL.Ontology))
g.add((ONTO_URI, RDFS.label, Literal("EU AI Act Ontology", lang="en")))
g.add((ONTO_URI, DCTERMS.description, Literal(
    "An OWL ontology capturing the key concepts, actors, and obligations of "
    "Regulation (EU) 2024/1689 (EU Artificial Intelligence Act)", lang="en")))
g.add((ONTO_URI, DCTERMS.source, URIRef(
    "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689")))
g.add((ONTO_URI, OWL.versionInfo, Literal("0.1.0")))

# ─── Top-Level Classes (manually curated, informed by GraphRAG clusters) ───────
TOP_CLASSES = {
    "AISystem": ("AI System",
        "A machine-based system designed to operate with varying levels of autonomy "
        "and that may exhibit adaptiveness after deployment. (Article 3(1))"),
    "HighRiskAISystem": ("High-Risk AI System",
        "An AI system listed in Annex III or embedded in a product covered by "
        "Union harmonisation legislation. (Article 6)"),
    "ProhibitedAIPractice": ("Prohibited AI Practice",
        "An AI practice that is banned under Article 5 due to unacceptable risk."),
    "GeneralPurposeAIModel": ("General-Purpose AI Model",
        "An AI model trained on large data that can perform a wide range of tasks. (Article 3(63))"),
    "SystemicRiskGPAI": ("General-Purpose AI Model with Systemic Risk",
        "A GPAI model designated as posing systemic risk, typically above 10^25 FLOPs. (Article 51)"),
    "Actor": ("Actor", "An entity with legal standing under the EU AI Act."),
    "Provider": ("Provider",
        "A natural or legal person that develops or places an AI system on the market. (Article 3(3))"),
    "Deployer": ("Deployer",
        "A natural or legal person that uses an AI system under their authority. (Article 3(4))"),
    "Importer": ("Importer", "A person in the Union who places an AI system from a third country on the market. (Article 3(6))"),
    "Distributor": ("Distributor", "A person in the supply chain other than provider/importer. (Article 3(7))"),
    "AuthorisedRepresentative": ("Authorised Representative", "A person in the Union mandated by a provider established outside the Union. (Article 3(5))"),
    "Authority": ("Regulatory Authority", "A body responsible for oversight, enforcement, or coordination of the Act."),
    "NationalCompetentAuthority": ("National Competent Authority",
        "A Member State authority designated to supervise application of the Act. (Article 70)"),
    "AIOffice": ("AI Office",
        "The Commission body responsible for GPAI model oversight and coordination. (Article 64)"),
    "EuropeanAIBoard": ("European AI Board",
        "Advisory body composed of Member State representatives. (Article 65)"),
    "NotifiedBody": ("Notified Body",
        "A conformity assessment body designated by a Member State. (Article 3(22))"),
    "Obligation": ("Obligation", "A duty, requirement, or prohibition imposed by the Act."),
    "TransparencyObligation": ("Transparency Obligation",
        "Obligations to inform users that they are interacting with an AI system. (Article 50)"),
    "ConformityAssessment": ("Conformity Assessment",
        "The process to demonstrate a high-risk AI system meets the requirements. (Article 43)"),
    "QualityManagementSystem": ("Quality Management System",
        "A system providers must establish to ensure compliance. (Article 17)"),
    "PostMarketMonitoring": ("Post-Market Monitoring",
        "Systematic collection and review of experience with deployed AI systems. (Article 72)"),
    "Requirement": ("Technical Requirement",
        "A technical or organisational requirement for high-risk AI systems."),
    "DataGovernance": ("Data Governance",
        "Requirements on training, validation and testing data. (Article 10)"),
    "HumanOversight": ("Human Oversight",
        "Measures enabling humans to oversee and intervene in AI system operation. (Article 14)"),
    "Robustness": ("Accuracy, Robustness and Cybersecurity",
        "Requirements for AI system performance and resilience. (Article 15)"),
    "TechnicalDocumentation": ("Technical Documentation",
        "Documentation providers must maintain before placing on the market. (Article 11, Annex IV)"),
    "RiskManagementSystem": ("Risk Management System",
        "A continuous iterative process to identify and mitigate risks. (Article 9)"),
    "RiskCategory": ("Risk Category", "A level of risk under the EU AI Act classification framework."),
}

def safe_uri(name):
    """Convert a label to a safe URI fragment."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name.strip())

# Add classes
for cls_id, (label, desc) in TOP_CLASSES.items():
    cls_uri = EU_AI[cls_id]
    g.add((cls_uri, RDF.type, OWL.Class))
    g.add((cls_uri, RDFS.label, Literal(label, lang="en")))
    g.add((cls_uri, SKOS.definition, Literal(desc, lang="en")))

# ─── Class Hierarchy ───────────────────────────────────────────────────────────
SUBCLASS_OF = [
    ("HighRiskAISystem", "AISystem"),
    ("ProhibitedAIPractice", "AISystem"),
    ("GeneralPurposeAIModel", "AISystem"),
    ("SystemicRiskGPAI", "GeneralPurposeAIModel"),
    ("Provider", "Actor"),
    ("Deployer", "Actor"),
    ("Importer", "Actor"),
    ("Distributor", "Actor"),
    ("AuthorisedRepresentative", "Actor"),
    ("NationalCompetentAuthority", "Authority"),
    ("AIOffice", "Authority"),
    ("EuropeanAIBoard", "Authority"),
    ("NotifiedBody", "Authority"),
    ("TransparencyObligation", "Obligation"),
    ("ConformityAssessment", "Obligation"),
    ("QualityManagementSystem", "Obligation"),
    ("PostMarketMonitoring", "Obligation"),
    ("DataGovernance", "Requirement"),
    ("HumanOversight", "Requirement"),
    ("Robustness", "Requirement"),
    ("TechnicalDocumentation", "Requirement"),
    ("RiskManagementSystem", "Requirement"),
]

for child, parent in SUBCLASS_OF:
    g.add((EU_AI[child], RDFS.subClassOf, EU_AI[parent]))

# ─── Object Properties ─────────────────────────────────────────────────────────
OBJECT_PROPS = {
    "hasObligation": ("has obligation",
        "Relates an actor to an obligation they must fulfil.",
        "Actor", "Obligation"),
    "hasRequirement": ("has requirement",
        "Relates a high-risk AI system to a technical requirement.",
        "AISystem", "Requirement"),
    "hasRiskCategory": ("has risk category",
        "Classifies an AI system into a risk category.",
        "AISystem", "RiskCategory"),
    "regulatedBy": ("regulated by",
        "Relates an actor or AI system to the authority overseeing it.",
        None, "Authority"),
    "enforces": ("enforces",
        "Relates an authority to the obligations it enforces.",
        "Authority", "Obligation"),
    "subjectTo": ("subject to",
        "Relates an AI system to an applicable obligation.",
        "AISystem", "Obligation"),
    "conductedBy": ("conducted by",
        "Relates a conformity assessment to the body conducting it.",
        "ConformityAssessment", "Actor"),
    "triggers": ("triggers",
        "Relates a risk category to the obligations it activates.",
        "RiskCategory", "Obligation"),
    "placeOnMarket": ("places on market",
        "Relates a provider to an AI system they make available.",
        "Provider", "AISystem"),
    "deploysSystem": ("deploys system",
        "Relates a deployer to an AI system they operate.",
        "Deployer", "AISystem"),
}

for prop_id, (label, desc, domain, range_) in OBJECT_PROPS.items():
    prop_uri = EU_AI[prop_id]
    g.add((prop_uri, RDF.type, OWL.ObjectProperty))
    g.add((prop_uri, RDFS.label, Literal(label, lang="en")))
    g.add((prop_uri, SKOS.definition, Literal(desc, lang="en")))
    if domain:
        g.add((prop_uri, RDFS.domain, EU_AI[domain]))
    if range_:
        g.add((prop_uri, RDFS.range, EU_AI[range_]))

# ─── Datatype Properties ────────────────────────��──────────────────────────────
DATA_PROPS = {
    "articleReference": ("article reference",
        "The article number(s) in the EU AI Act where this concept is defined."),
    "riskLevel": ("risk level",
        "The risk level designation (unacceptable/high/limited/minimal)."),
    "annexReference": ("annex reference",
        "Reference to a relevant Annex of the EU AI Act."),
}

for prop_id, (label, desc) in DATA_PROPS.items():
    prop_uri = EU_AI[prop_id]
    g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
    g.add((prop_uri, RDFS.label, Literal(label, lang="en")))
    g.add((prop_uri, SKOS.definition, Literal(desc, lang="en")))
    g.add((prop_uri, RDFS.range, XSD.string))

# ─── Named Individuals (from GraphRAG + manual curation) ───────────────────────
INDIVIDUALS = [
    # Prohibited practices (Article 5)
    ("SubliminaltechniquesAI", "ProhibitedAIPractice",
     "AI using subliminal techniques to distort behaviour causing harm", "Article 5(1)(a)"),
    ("ExploitativeAI", "ProhibitedAIPractice",
     "AI exploiting vulnerabilities of specific groups", "Article 5(1)(b)"),
    ("SocialScoringPublicAuthority", "ProhibitedAIPractice",
     "Social scoring by public authorities leading to detrimental treatment", "Article 5(1)(c)"),
    ("RealTimeBiometricSurveillance", "ProhibitedAIPractice",
     "Real-time remote biometric identification in publicly accessible spaces (with narrow exceptions)", "Article 5(1)(h)"),
    # High-risk system categories (Annex III)
    ("BiometricIdentificationSystem", "HighRiskAISystem",
     "AI systems for biometric identification of persons", "Annex III, 1"),
    ("CriticalInfrastructureAI", "HighRiskAISystem",
     "AI for management and operation of critical infrastructure", "Annex III, 2"),
    ("EducationAdmissionAI", "HighRiskAISystem",
     "AI determining access to educational institutions", "Annex III, 3"),
    ("EmploymentAI", "HighRiskAISystem",
     "AI for recruitment and employment decisions", "Annex III, 4"),
    ("EssentialServicesAI", "HighRiskAISystem",
     "AI for access to essential private and public services", "Annex III, 5"),
    ("LawEnforcementAI", "HighRiskAISystem",
     "AI used by law enforcement authorities", "Annex III, 6"),
    ("MigrationAsylumAI", "HighRiskAISystem",
     "AI for migration, asylum and border control", "Annex III, 7"),
    ("JusticeAI", "HighRiskAISystem",
     "AI assisting judicial authorities in legal research and decisions", "Annex III, 8"),
    # Risk categories
    ("UnacceptableRisk", "RiskCategory",
     "Risk level triggering an outright prohibition", "Article 5"),
    ("HighRisk", "RiskCategory",
     "Risk level triggering the full set of Chapter III obligations", "Article 6"),
    ("LimitedRisk", "RiskCategory",
     "Risk level triggering transparency obligations only", "Article 50"),
    ("MinimalRisk", "RiskCategory",
     "Risk level with no mandatory obligations under the Act", "Recital 46"),
]

for ind_id, cls_id, desc, article_ref in INDIVIDUALS:
    ind_uri = EU_AI[safe_uri(ind_id)]
    g.add((ind_uri, RDF.type, OWL.NamedIndividual))
    g.add((ind_uri, RDF.type, EU_AI[cls_id]))
    g.add((ind_uri, RDFS.label, Literal(ind_id, lang="en")))
    g.add((ind_uri, SKOS.definition, Literal(desc, lang="en")))
    g.add((ind_uri, EU_AI["articleReference"], Literal(article_ref)))

# ─── Add GraphRAG-extracted entities dynamically ───────────────────────────────
try:
    entities_df = pd.read_parquet("graphrag/output/entities.parquet")
    # GraphRAG v3 stores types in UPPERCASE — map to ontology class names
    type_map = {
        "AISYSTEM": "AISystem",
        "ACTOR": "Actor",
        "OBLIGATION": "Obligation",
        "AUTHORITY": "Authority",
        "REQUIREMENT": "Requirement",
        "RISKCATEGORY": "RiskCategory",
        "ARTICLE": "Article",
        "ANNEXIIICATEGORY": "AnnexIIICategory",
        "EXCLUSIONCONDITION": "ExclusionCondition",
        "CLASSIFICATIONRULE": "ClassificationRule",
        "DELEGATEDACT": "DelegatedAct",
        "SYSTEMICRISK": "SystemicRisk",
        "CODEOFPRACTICE": "CodeOfPractice",
        "SERIOUSINCIDENT": "SeriousIncident",
        "COMPLAINT": "Complaint",
    }

    # Ensure extra classes exist for types not in TOP_CLASSES
    extra_classes = {
        "Article": "A reference to a specific article, annex, or recital of the EU AI Act.",
        "AnnexIIICategory": "One of the 8 high-risk use case domains listed in Annex III.",
        "ExclusionCondition": "A condition under which an Annex III AI system is NOT classified as high-risk.",
        "ClassificationRule": "A rule or criterion determining whether an AI system is classified as high-risk.",
        "DelegatedAct": "A Commission act that modifies or extends classification rules or obligations.",
        "SystemicRisk": "Risk classification for GPAI models exceeding the compute threshold.",
        "CodeOfPractice": "A voluntary compliance instrument for GPAI model providers.",
        "SeriousIncident": "An event related to a GPAI model that must be reported.",
        "Complaint": "A formal instrument for downstream providers to report upstream infringements.",
    }
    for cls_id, desc in extra_classes.items():
        cls_uri = EU_AI[cls_id]
        if (cls_uri, RDF.type, OWL.Class) not in g:
            g.add((cls_uri, RDF.type, OWL.Class))
            g.add((cls_uri, RDFS.label, Literal(cls_id, lang="en")))
            g.add((cls_uri, SKOS.definition, Literal(desc, lang="en")))

    added_count = 0
    for _, row in entities_df.iterrows():
        entity_type = type_map.get(str(row.get('type', '')).upper())
        if entity_type and pd.notna(row.get('title')):
            uri = EU_AI[safe_uri(str(row['title']))]
            g.add((uri, RDF.type, OWL.NamedIndividual))
            g.add((uri, RDF.type, EU_AI[entity_type]))
            g.add((uri, RDFS.label, Literal(str(row['title']), lang="en")))
            if pd.notna(row.get('description')):
                g.add((uri, SKOS.definition, Literal(str(row['description'])[:500], lang="en")))
            added_count += 1
    print(f"Added {added_count} GraphRAG entities (out of {len(entities_df)} total)")
except FileNotFoundError:
    print("GraphRAG output not yet available — using manually defined individuals only")

# ─── Add GraphRAG-extracted relationships dynamically ──────────────────────────
try:
    rels_df = pd.read_parquet("graphrag/output/relationships.parquet")
    rel_count = 0
    for _, row in rels_df.iterrows():
        if pd.notna(row.get('source')) and pd.notna(row.get('target')):
            src_uri = EU_AI[safe_uri(str(row['source']))]
            tgt_uri = EU_AI[safe_uri(str(row['target']))]
            desc = str(row.get('description', '')) if pd.notna(row.get('description')) else ''

            # Try to detect the relationship type from the description
            rel_type = "relatedTo"  # fallback
            for known_rel in [
                "hasObligation", "hasRiskCategory", "definedInArticle", "regulatedBy",
                "subjectTo", "enforces", "triggers", "hasException", "hasDeadline",
                "hasConsequence", "grants", "rejects", "isExemptFromHighRisk",
                "alwaysClassifiedAs", "belongsToCategory", "appliesTo", "modifies",
                "providesInstructionsTo", "appliesThroughout", "isBasedOn",
                "cooperatesWith", "meetsSystemicRiskThreshold", "notifiesWithin",
                "presumesConformity", "lodgesComplaintWith", "conductsEvaluationOf",
                "reducedObligationsApplyTo",
            ]:
                if known_rel.lower() in desc.lower():
                    rel_type = known_rel
                    break

            prop_uri = EU_AI[rel_type]
            # Ensure the object property exists
            if (prop_uri, RDF.type, OWL.ObjectProperty) not in g:
                g.add((prop_uri, RDF.type, OWL.ObjectProperty))
                g.add((prop_uri, RDFS.label, Literal(rel_type, lang="en")))

            g.add((src_uri, prop_uri, tgt_uri))

            # Attach the description as an annotation on a reified statement
            if desc:
                # Use a simple annotation on the source
                pass  # description is captured via the property; keeping triples lean

            rel_count += 1
    print(f"Added {rel_count} GraphRAG relationships")
except FileNotFoundError:
    print("GraphRAG relationships not found — skipping")

# ─── Post-process: add labels to any URI that lacks one ────────────────────────
# This fixes SHACL violations where relationship targets exist as URIs but were
# never extracted as standalone entities (so they have no rdfs:label).
unlabelled_count = 0
all_uris = set(g.subjects()) | set(g.objects())
for node in all_uris:
    if isinstance(node, URIRef) and str(node).startswith(str(EU_AI)):
        if (node, RDFS.label, None) not in g:
            # Derive a human-readable label from the URI fragment
            fragment = str(node).replace(str(EU_AI), "")
            label = fragment.replace("_", " ").strip()
            if label:
                g.add((node, RDFS.label, Literal(label, lang="en")))
                unlabelled_count += 1
if unlabelled_count:
    print(f"Added labels to {unlabelled_count} previously unlabelled URIs")

# ─── Serialise ─────────────────────────────────────────────────────────────────
import os
os.makedirs("ontology", exist_ok=True)
g.serialize("ontology/eu-ai-act.ttl", format="turtle")
g.serialize("ontology/eu-ai-act.owl", format="xml")
print(f"Ontology written: {len(g)} triples")