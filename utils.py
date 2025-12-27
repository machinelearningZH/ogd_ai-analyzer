import pandas as pd
import os
import re
import yaml
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Load configuration from YAML
with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as f:
    config = yaml.safe_load(f)

LLM_MODEL_ID = config["llm_model_id"]
MAX_TOKENS = config["max_tokens"]

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)


def call_openrouter(prompt, modelId=None, max_tokens=None):
    # Use config defaults if not specified
    if modelId is None:
        modelId = LLM_MODEL_ID
    if max_tokens is None:
        max_tokens = MAX_TOKENS
    try:
        completion = openai_client.chat.completions.create(
            model=modelId,
            max_completion_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content

    except Exception as e:
        print(f"Error: {e}")
        return None


PROMPT_ANOMALIES = """
Du bist Datenqualitätsprüfer für einen Datenkatalog eines Schweizer Statistikamts. Analysiere die {feature}-Werte auf Anomalien und Auffälligkeiten.

Daten:
<datensatz_{feature}>
{data}
</datensatz_{feature}>

Aufgabe:
1. Identifiziere alle Anomalien in den {feature}-Werten
2. Dokumentiere jede Anomalie mit 1–3 konkreten Beispielen (exakte Originalwerte)
3. Bei Rechtschreib-/Tippfehlern oder inkonsistenten Schreibweisen: alle Beispiele angeben
4. Falls keine Anomalien: schreibe nur "Keine Anomalien erkennbar."

Typische Anomalie-Kategorien (nur nennen, wenn zutreffend):
- Rechtschreib-, Grammatik- oder Tippfehler
- Inkonsistente Schreibweisen oder Terminologie
- Unklare, mehrdeutige oder unvollständige Formulierungen
- Uneinheitliche Sprache oder Einheiten
- Verdächtige Muster (Template-Reste, Lorem ipsum, Copy-Paste-Fehler)

Output-Format (Markdown):
### <Anomalie-Kategorie>
- Beispiele: "<wert1>", "<wert2>", "<wert3>"

Schreibe auf Deutsch. Beginne direkt mit der Analyse, ohne Einleitung oder Schlussbemerkung.
""".strip()


def check_text_properties(feature, data):
    """Check the text properties of the titles and descriptions of the datasets globally. Each will be provided to the LLM as a comma-separated list. The analysis will be done in one go, not per dataset."""
    return call_openrouter(PROMPT_ANOMALIES.format(feature=feature, data=data))


SYSTEM_MESSAGE = """"Du bist ein hilfreicher Assistent für ein Statistikamt. Du wirst gebeten, Metadaten für einen Datensatz zu analysieren. Bleibe stets wahrheitsgemäß und objektiv. Schreib nur das, was du anhand der vom Benutzer bereitgestellten Metadaten sicher feststellen kannst. Mache keine Annahmen. Schreibe einfach und klar. Schreibe immer in deutscher Sprache."""

PROMPT_ANALYSIS = """Du erhältst die Metadaten eines Datensatzes. Diese sollst du detailliert und genau analysieren. Die Metadaten bestehen aus einem Titel und einer Beschreibung. Du sollst die Metadaten analysieren und sicherstellen, dass diese aussagekräftig, vollständig und von hoher Qualität sind.

Analysiere Schritt für Schritt die Metadaten nach folgenden Kriterien:

    1. Dateninhalt - Wie detailliert und eindeutig erklären Titel und Beschreibung, worum es in dem Datensatz geht?
    2. Methodik - Wie detailliert und eindeutig erklären Titel und Beschreibung, wie die Daten gemessen wurden und wofür? Wird die Quelle der Daten genannt und beschrieben?
    3. Datenqualität - Wie detailliert und eindeutig erklären Titel und Beschreibung, wie gut die Qualität der Daten ist? Wird erklärt, wie vollständig die Daten sind? Gibt es Änderungen in der Erhebung? 
    4. Geographie - Wie detailliert und eindeutig erklären Titel und Beschreibung, wie die Daten geographisch zu verstehen sind? Wird klar, auf welche geographischen Orte oder Gebiete sich die Daten beziehen? 

Prüfe bei jedem Punkt auch, ob es Auffälligkeiten oder Anomalien gibt und bennene diese kurz. Das können zum Beispiel sein: 
    - fehlende Informationen, 
    - schwer verständliche oder vieldeutige Begriffe,
    - unnötige und unklare Abkürzungen,
    - Rechtschreibfehler oder uneinheitliche Schreibweisen,
    - ungewöhnliche Zeichen, Symbole oder Formatierungen,
    - Tags, Markdown, HTML-Code oder andere Programmierzeichen,
    - unklare oder unvollständige Sätze oder Absätze,
    - keine geschlechtergerechte Sprache.

Hier ein Beispiel:

    Titel: Web Analytics der Open Government Data des Kantons Zürich auf opendata.swiss von Februar 2018 bis Februar 2021
    Beschreibung: Monatliche Nutzungsstatistiken (Anzahl Besuche) der Open Government Data (OGD) Metadatensätze von Verwaltungseinheiten und Organen des Kantons Zürich, die auf dem zentralen Katalog für offene Behördendaten opendata.swiss findbar sind. Hinweise: Ab Januar 2019 sind die Web Analytics um weitere Metadateninformationen erweitert bzw. wurden Metadatenanpassungen vorgenommen. Ab März 2021 sind die monatlichen Aktualisierungen aufgrund technischer Herausforderungen pausiert. Variablendefinitionen: Column 'name' = dataset slug; 'issued' = first publication of dataset; 'organization_name' = publisher slug; 'organization_url' = publisher URL; 'E' up to 'AB' = thematic categories according to DCAT AP Switzerland.

    Dateninhalt: Detaillierte und eindeutige Erklärung, worum es in dem Datensatz geht.
    Methodik: Detaillierte und eindeutige Erklärung, wie die Daten gemessen wurden und wofür. Variablendefinitionen sind klar und detailliert. -> 4 Punkte
    Datenqualität: Einige Hinweise auf die Qualität der Daten, ebenso Angaben zur Vollständigkeit und zu Änderungen in der Erhebung. -> 4 Punkte
    Geographie: Keine spezifischen Angaben zu geographischen Orten oder Gebieten. -> 1 Punkt

Hier ein weiteres Beispiel:

    Titel: Kühe [Anz.]
    Beschreibung: Anzahl Kühe

    Dateninhalt: Es ist nicht klar, welche Daten genau erfasst werden. Eine detaillierte Beschreibung der Daten fehlt völlig. -> 2 Punkte
    Methodik: Es gibt keine Informationen darüber, wie die Daten gemessen wurden und wofür. -> 1 Punkt
    Datenqualität: Es gibt keine Informationen zur Qualität der Daten. -> 1 Punkt
    Geographie: Es gibt keine Informationen zum räumlichen Bezug. -> 1 Punkt


Gibt das Ergebnis deiner Analyse in XML-Tags aus, in dieser Form:

<dateninhalt> ... </dateninhalt>
<methodik> ... </methodik>
<datenqualität> ... </datenqualität>
<geographie> ... </geographie>

Vergib dann eine Bewertung für jedes der vier Kriterien. 
Verwende die Skala von 1-5, wobei 1 die schlechteste und 5 die beste Bewertung ist.
Sei klar, hart und kritisch bei deiner Bewertung. 
Hier ist die Bewertungsskala:

1 Punkt - Keine Informationen zu diesem Kriterium.
2 Punkte - Wenige Informationen, viel fehlt.
3 Punkte - Mittelmässige Informationen, einige Informationen sind vorhanden, einiges fehlt.
4 Punkte - Gute Informationen, die meisten Informationen sind vorhanden.
5 Punkte - Exzellente Informationen, alles ist sehr klar, vollständig und detailliert.

Gib die Bewertung in XML-Tags aus, in dieser Form:

<dateninhalt-score> ... </dateninhalt-score>
<methodik-score> ... </methodik-score>
<datenqualität-score> ... </datenqualität-score>
<geographie-score> ... </geographie-score>

Analysiere und bewerte jetzt die Metadaten des Datensatzes.

Hier sind die Metadaten des Datensatzes, den du analysieren sollst:
---------------------------------------------------------------------

Titel: {title}
Beschreibung: {description}
"""


def do_full_analysis(data):
    """Check the titles and descriptions of each dataset individually."""
    return call_openrouter(
        PROMPT_ANALYSIS.format(title=data.title, description=data.description)
    )


def parse_analysis_results(results):
    """Parse the LLM response. Extract the scores and the qualitative analysis.

    Args:
        results (str): The response from the LLM.

    Returns:
        pd.DataFrame: A DataFrame with the scores and the qualitative analysis.

    """
    def extract_tag(pattern, text, default=""):
        """Extract content from XML tags with fallback to default."""
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[0].strip() if matches else default
    
    content = extract_tag(r"<dateninhalt>(.*?)</dateninhalt>", results)
    content_score = extract_tag(r"<dateninhalt-score>(.*?)</dateninhalt-score>", results)
    context = extract_tag(r"<methodik>(.*?)</methodik>", results)
    context_score = extract_tag(r"<methodik-score>(.*?)</methodik-score>", results)
    quality = extract_tag(r"<datenqualität>(.*?)</datenqualität>", results)
    quality_score = extract_tag(r"<datenqualität-score>(.*?)</datenqualität-score>", results)
    spatial = extract_tag(r"<geographie>(.*?)</geographie>", results)
    spatial_score = extract_tag(r"<geographie-score>(.*?)</geographie-score>", results)
    
    tmp = pd.DataFrame(
        (
            content,
            content_score,
            context,
            context_score,
            quality,
            quality_score,
            spatial,
            spatial_score,
        )
    ).T
    tmp.columns = [
        "content",
        "content_score",
        "context",
        "context_score",
        "quality",
        "quality_score",
        "spatial",
        "spatial_score",
    ]
    return tmp


# Data derived from the DCAT-AP CH specification here:
# https://www.dcat-ap.ch/releases/2.0/dcat-ap-ch.html#Class:Dataset
DCAT_CLASS_DATASET = [
    ("contact point", "dcat:contactPoint", "vcard:Kind", "M", "1..n"),
    ("description", "dct:description", "rdfs:Literal", "M", "1..n"),
    ("identifier", "dct:identifier", "rdfs:Literal", "M", "1..n"),
    ("publisher", "dct:publisher", "foaf:Agent", "M", "1..1"),
    ("Title", "dct:title", "rdfs:Literal", "M", "1..n"),
    ("dataset distribution", "dcat:distribution", "dcat:Distribution", "R", "0..n"),
    ("keyword/tag", "dcat:keyword", "rdfs:Literal", "R", "0..n"),
    ("landing page", "dcat:landingPage", "foaf:Document", "R", "0..n"),
    (
        "release date",
        "dct:issued",
        "rdfs:Literal (typed as xsd:date, xsd:dateTime, xsd:gYear or xsd:gYearMonth)",
        "R",
        "0..1",
    ),
    ("spatial/ geographical coverage", "dct:spatial", "dct:Location", "R", "0..n"),
    ("temporal coverage", "dct:temporal", "dct:PeriodOfTime", "R", "0..n"),
    ("theme/category", "dcat:theme", "skos:Concept", "R", "0..n"),
    (
        "update/ modification date",
        "dct:modified",
        "rdfs:Literal (typed as xsd:date, xsd:dateTime, xsd:gYear or xsd:gYearMonth)",
        "R",
        "0..1",
    ),
    ("access rights", "dct:accessRights", "dct:RightsStatement", "O", "0..1"),
    ("conforms to", "dct:conformsTo", "dct:Standard", "O", "0..n"),
    ("documentation", "foaf:page", "foaf:Document", "O", "0..n"),
    ("frequency", "dct:accrualPeriodicity", "dct:Frequency", "O", "0..1"),
    ("image", "schema:image", "schema:url or schema:ImageObject", "O", "0..3"),
    ("is referenced by", "dct:isReferencedBy", "rdfs:Resource", "O", "0..n"),
    ("language", "dct:language", "dct:LinguisticSystem", "O", "0..n"),
    (
        "qualified attribution",
        "prov:qualifiedAttribution",
        "prov:Attribution",
        "O",
        "0..n",
    ),
    ("qualified relation", "dcat:qualifiedRelation", "dcat:Relationship", "O", "0..n"),
    ("related resource", "dct:relation", "rdfs:Resource", "O", "0..n"),
]

DCAT_CLASS_DISTRIBUTION = data = [
    ("dcat:accessURL", "rdfs:Resource", "M", "1..n"),
    ("dct:license", "dct:LicenseDocument", "M", "1..1"),
    ("dcatap:availability", "skos:Concept", "R", "0..1"),
    ("dct:description", "rdfs:Literal", "R", "0..n"),
    ("dct:format", "dct:MediaTypeOrExtent", "R", "0..1"),
    ("dct:rights", "dct:RightsStatement", "R", "0..1"),
    ("dct:title", "rdfs:Literal", "R", "0..n"),
    (
        "dct:modified",
        "rdfs:Literal (typed as xsd:date, xsd:dateTime, xsd:gYear or xsd:gYearMonth)",
        "R",
        "0..1",
    ),
    ("dcat:accessService", "dcat:DataService", "O", "0..n"),
    ("dcat:byteSize", "rdfs:Literal (typed as xsd:decimal)", "O", "0..1"),
    ("spdx:checksum", "spdx:Checksum", "O", "0..1"),
    ("dct:coverage", "LocationPeriodOrJurisdiction", "O", "0..n"),
    ("foaf:page", "foaf:Document", "O", "0..n"),
    ("dcat:downloadURL", "rdfs:Resource", "O", "0..n"),
    ("dct:identifier", "rdfs:Literal", "O", "0..1"),
    ("schema:image", "schema:url or schema:ImageObject", "O", "0..3"),
    ("dct:language", "dct:LinguisticSystem", "O", "0..n"),
    ("dct:conformsTo", "dct:Standard", "O", "0..n"),
    ("dcat:mediaType", "dct:MediaType", "O", "0..1"),
    ("dcat:packageFormat", "dcat:mediaType", "O", "0..1"),
    (
        "dct:issued",
        "rdfs:Literal (typed as xsd:date, xsd:dateTime, xsd:gYear or xsd:gYearMonth)",
        "R",
        "0..1",
    ),
    ("dcat:temporalResolution", "xsd:duration", "R", "0..1"),
]


# Data derived from here:
# https://publications.europa.eu/resource/authority/data-theme
VOCAB_EU_THEME = [
    "http://publications.europa.eu/resource/authority/data-theme/TECH",
    "http://publications.europa.eu/resource/authority/data-theme/TRAN",
    "http://publications.europa.eu/resource/authority/data-theme/REGI",
    "http://publications.europa.eu/resource/authority/data-theme/SOCI",
    "http://publications.europa.eu/resource/authority/data-theme/AGRI",
    "http://publications.europa.eu/resource/authority/data-theme/ECON",
    "http://publications.europa.eu/resource/authority/data-theme/JUST",
    "http://publications.europa.eu/resource/authority/data-theme/OP_DATPRO",
    "http://publications.europa.eu/resource/authority/data-theme/HEAL",
    "http://publications.europa.eu/resource/authority/data-theme/INTR",
    "http://publications.europa.eu/resource/authority/data-theme/ENVI",
    "http://publications.europa.eu/resource/authority/data-theme/GOVE",
    "http://publications.europa.eu/resource/authority/data-theme/EDUC",
    "http://publications.europa.eu/resource/authority/data-theme/ENER",
]

# Data derived from here:
# https://publications.europa.eu/resource/authority/frequency
VOCAB_EU_FREQUENCY = [
    "http://publications.europa.eu/resource/authority/frequency/BIDECENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/TRIDECENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/BIHOURLY",
    "http://publications.europa.eu/resource/authority/frequency/TRIHOURLY",
    "http://publications.europa.eu/resource/authority/frequency/OTHER",
    "http://publications.europa.eu/resource/authority/frequency/WEEKLY",
    "http://publications.europa.eu/resource/authority/frequency/HOURLY",
    "http://publications.europa.eu/resource/authority/frequency/QUADRENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/QUINQUENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/DECENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/WEEKLY_2",
    "http://publications.europa.eu/resource/authority/frequency/WEEKLY_3",
    "http://publications.europa.eu/resource/authority/frequency/UNKNOWN",
    "http://publications.europa.eu/resource/authority/frequency/UPDATE_CONT",
    "http://publications.europa.eu/resource/authority/frequency/QUARTERLY",
    "http://publications.europa.eu/resource/authority/frequency/TRIENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/NEVER",
    "http://publications.europa.eu/resource/authority/frequency/OP_DATPRO",
    "http://publications.europa.eu/resource/authority/frequency/MONTHLY_2",
    "http://publications.europa.eu/resource/authority/frequency/MONTHLY_3",
    "http://publications.europa.eu/resource/authority/frequency/IRREG",
    "http://publications.europa.eu/resource/authority/frequency/MONTHLY",
    "http://publications.europa.eu/resource/authority/frequency/DAILY",
    "http://publications.europa.eu/resource/authority/frequency/DAILY_2",
    "http://publications.europa.eu/resource/authority/frequency/BIWEEKLY",
    "http://publications.europa.eu/resource/authority/frequency/CONT",
    "http://publications.europa.eu/resource/authority/frequency/BIENNIAL",
    "http://publications.europa.eu/resource/authority/frequency/BIMONTHLY",
    "http://publications.europa.eu/resource/authority/frequency/ANNUAL_2",
    "http://publications.europa.eu/resource/authority/frequency/ANNUAL_3",
    "http://publications.europa.eu/resource/authority/frequency/ANNUAL",
    "http://publications.europa.eu/resource/authority/frequency/NOT_PLANNED",
    "http://publications.europa.eu/resource/authority/frequency/AS_NEEDED",
]

# These are values for «hidden» nulls. These values satisfy the DCAT standard, because they are not empty. However, they are not useful or meaningful.
HIDDEN_NULLS = (
    "",
    "null",
    "[]",
    "{}",
    "nan",
    "none",
    "ohne angabe",
    "keine angabe",
    "nichts",
)
