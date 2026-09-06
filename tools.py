import os
import requests

from dotenv import load_dotenv
from langchain.tools import tool


load_dotenv()

SMITHSONIAN_API_KEY = os.getenv("SMITHSONIAN_API_KEY")
EUROPEANA_API_KEY = os.getenv("EUROPEANA_API_KEY")


# ============================================================
# HELPER
# ============================================================

def clean_text(value, max_length=500):
    """
    Convert API values into readable text.
    """

    if value is None:
        return "Not available"

    if isinstance(value, list):
        value = ", ".join(
            str(item) for item in value[:5]
        )

    value = str(value).strip()

    if not value:
        return "Not available"

    return value[:max_length]


# ============================================================
# TOOL 1: MUSEUM / ARTIFACT SEARCH
# ============================================================

@tool
def artifact_search(query: str) -> str:
    """
    Search real museum and cultural heritage collections
    using Smithsonian Open Access and Europeana.

    Returns collection metadata that can be used as
    evidence for historical investigation.
    """

    results = []

    # ========================================================
    # SMITHSONIAN
    # ========================================================

    if SMITHSONIAN_API_KEY:

        smithsonian_url = (
            "https://api.si.edu/openaccess/api/v1.0/search"
        )

        smithsonian_params = {
            "q": query,
            "api_key": SMITHSONIAN_API_KEY,
            "rows": 5
        }

        try:

            response = requests.get(
                smithsonian_url,
                params=smithsonian_params,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            records = data.get(
                "response",
                {}
            ).get(
                "rows",
                []
            )

            if records:

                results.append(
                    "===== SMITHSONIAN EVIDENCE ====="
                )

                for index, record in enumerate(
                    records,
                    start=1
                ):

                    title = clean_text(
                        record.get("title")
                    )

                    url = clean_text(
                        record.get("url")
                    )

                    content = record.get(
                        "content",
                        {}
                    )

                    descriptive = content.get(
                        "descriptiveNonRepeating",
                        {}
                    )

                    record_id = clean_text(
                        descriptive.get("record_ID")
                    )

                    unit_code = clean_text(
                        descriptive.get("unit_code")
                    )

                    data_source = clean_text(
                        descriptive.get("data_source")
                    )

                    freetext = content.get(
                        "freetext",
                        {}
                    )

                    notes = clean_text(
                        freetext.get("notes")
                    )

                    object_type = clean_text(
                        freetext.get("object_type")
                    )

                    materials = clean_text(
                        freetext.get("physicalDescription")
                    )

                    results.append(
                        f"""
Result {index}
Title: {title}
Record ID: {record_id}
Collection: {data_source}
Unit: {unit_code}
Object Type: {object_type}
Physical Description: {materials}
Notes: {notes}
Source URL: {url}
""".strip()
                    )

            else:

                results.append(
                    "Smithsonian: No matching records found."
                )

        except requests.RequestException as error:

            results.append(
                f"Smithsonian search failed: {error}"
            )

    else:

        results.append(
            "Smithsonian API key is not configured."
        )

    # ========================================================
    # EUROPEANA
    # ========================================================

    if EUROPEANA_API_KEY:

        europeana_url = (
            "https://api.europeana.eu/record/v2/search.json"
        )

        europeana_headers = {
            "X-Api-Key": EUROPEANA_API_KEY
        }

        europeana_params = {
            "query": query,
            "rows": 5
        }

        try:

            response = requests.get(
                europeana_url,
                headers=europeana_headers,
                params=europeana_params,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            records = data.get(
                "items",
                []
            )

            if records:

                results.append(
                    "\n===== EUROPEANA EVIDENCE ====="
                )

                for index, record in enumerate(
                    records[:5],
                    start=1
                ):

                    titles = record.get(
                        "title",
                        []
                    )

                    if isinstance(titles, list) and titles:
                        title = clean_text(titles[0])
                    else:
                        title = "Not available"

                    provider = clean_text(
                        record.get("dataProvider")
                    )

                    record_id = clean_text(
                        record.get("id")
                    )

                    descriptions = record.get(
                        "dcDescription",
                        []
                    )

                    if (
                        isinstance(descriptions, list)
                        and descriptions
                    ):
                        description = clean_text(
                            descriptions[0]
                        )
                    else:
                        description = "Not available"

                    types = record.get(
                        "type",
                        "Not available"
                    )

                    countries = record.get(
                        "country",
                        []
                    )

                    country = clean_text(
                        countries
                    )

                    results.append(
                        f"""
Result {index}
Title: {title}
Provider: {provider}
Type: {types}
Country: {country}
Description: {description}
Europeana ID: {record_id}
""".strip()
                    )

            else:

                results.append(
                    "Europeana: No matching records found."
                )

        except requests.RequestException as error:

            results.append(
                f"Europeana search failed: {error}"
            )

    else:

        results.append(
            "Europeana API key is not configured."
        )

    return "\n\n".join(results)


# ============================================================
# TOOL 2: HISTORICAL KNOWLEDGE SEARCH
# ============================================================

@tool
def historical_search(query: str) -> str:
    """
    Search Wikidata for historical entities related to
    an artifact, material, object type, culture, or period.
    """

    url = "https://www.wikidata.org/w/api.php"

    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "limit": 5
    }

    headers = {
        "User-Agent": (
            "ArtifactHistoryInvestigator/1.0 "
            "(educational project)"
        )
    }

    try:

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as error:

        return f"Wikidata search failed: {error}"

    records = data.get(
        "search",
        []
    )

    if not records:

        return (
            "No matching historical entities "
            "were found in Wikidata."
        )

    results = [
        "===== WIKIDATA EVIDENCE ====="
    ]

    for index, record in enumerate(
        records,
        start=1
    ):

        label = clean_text(
            record.get("label")
        )

        description = clean_text(
            record.get("description")
        )

        entity_id = clean_text(
            record.get("id")
        )

        entity_url = (
            f"https://www.wikidata.org/wiki/{entity_id}"
            if entity_id != "Not available"
            else "Not available"
        )

        results.append(
            f"""
Result {index}
Label: {label}
Description: {description}
Wikidata ID: {entity_id}
Source URL: {entity_url}
""".strip()
        )

    return "\n\n".join(results)


# ============================================================
# TOOL 3: TIMELINE ANALYSIS
# ============================================================

@tool
def timeline_tool(
    start_year: int,
    end_year: int
) -> str:
    """
    Calculate an approximate age range from a proposed
    historical period.
    """

    current_year = 2026

    if start_year > end_year:

        return (
            "Invalid historical period. "
            "Start year must be earlier than end year."
        )

    youngest_age = current_year - end_year
    oldest_age = current_year - start_year

    return (
        f"Historical period: {start_year}–{end_year}\n"
        f"Approximate age range: "
        f"{youngest_age}–{oldest_age} years."
    )