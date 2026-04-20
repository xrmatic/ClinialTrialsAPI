import azure.functions as func
import logging
import requests
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

CLINICAL_TRIALS_API_URL = "https://clinicaltrials.gov/api/v2/studies"


@app.route(route="studies", methods=["GET"])
def search_clinical_trials(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function that searches ClinicalTrials.gov studies by a keyword.

    Query Parameters:
        search.term (str): The keyword to search for in ClinicalTrials.gov.
        pageSize (int, optional): Number of results per page (default: 10, max: 1000).
        pageToken (str, optional): Token for retrieving the next page of results.

    Returns:
        HttpResponse: JSON response containing matching studies or an error message.
    """
    logging.info("Received request to search clinical trials.")

    search_term = req.params.get("search.term")
    if not search_term:
        return func.HttpResponse(
            json.dumps({"error": "Missing required query parameter: 'search.term'"}),
            status_code=400,
            mimetype="application/json",
        )

    page_size_str = req.params.get("pageSize", "10")
    try:
        page_size = int(page_size_str)
        if page_size < 1 or page_size > 1000:
            raise ValueError("pageSize out of range")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid 'pageSize': must be an integer between 1 and 1000."}),
            status_code=400,
            mimetype="application/json",
        )

    page_token = req.params.get("pageToken")

    params = {
        "query.term": search_term,
        "pageSize": page_size,
        "format": "json",
    }
    if page_token:
        params["pageToken"] = page_token

    try:
        response = requests.get(CLINICAL_TRIALS_API_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logging.error("Request to ClinicalTrials.gov timed out.")
        return func.HttpResponse(
            json.dumps({"error": "The request to ClinicalTrials.gov timed out."}),
            status_code=504,
            mimetype="application/json",
        )
    except requests.exceptions.RequestException as e:
        logging.error("Error calling ClinicalTrials.gov API: %s", e)
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve data from ClinicalTrials.gov.", "details": str(e)}),
            status_code=502,
            mimetype="application/json",
        )

    try:
        data = response.json()
    except ValueError as e:
        logging.error("Failed to parse JSON response: %s", e)
        return func.HttpResponse(
            json.dumps({"error": "Failed to parse response from ClinicalTrials.gov."}),
            status_code=502,
            mimetype="application/json",
        )

    studies = data.get("studies", [])
    next_page_token = data.get("nextPageToken")

    result = {
        "searchTerm": search_term,
        "totalCount": data.get("totalCount"),
        "nextPageToken": next_page_token,
        "studies": [_parse_study(s) for s in studies],
    }

    return func.HttpResponse(
        json.dumps(result, indent=2),
        status_code=200,
        mimetype="application/json",
    )


def _parse_study(study: dict) -> dict:
    """Extract key fields from a ClinicalTrials.gov study object."""
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status_module = protocol.get("statusModule", {})
    description_module = protocol.get("descriptionModule", {})
    conditions_module = protocol.get("conditionsModule", {})
    contacts_module = protocol.get("contactsLocationsModule", {})

    return {
        "nctId": identification.get("nctId"),
        "briefTitle": identification.get("briefTitle"),
        "officialTitle": identification.get("officialTitle"),
        "overallStatus": status_module.get("overallStatus"),
        "startDate": status_module.get("startDateStruct", {}).get("date"),
        "completionDate": status_module.get("completionDateStruct", {}).get("date"),
        "briefSummary": description_module.get("briefSummary"),
        "conditions": conditions_module.get("conditions", []),
        "centralContacts": [
            {
                "name": c.get("name"),
                "phone": c.get("phone"),
                "email": c.get("email"),
            }
            for c in contacts_module.get("centralContacts", [])
        ],
    }
