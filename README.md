# ClinicalTrialsAPI

An Azure Function that searches [ClinicalTrials.gov](https://clinicaltrials.gov/) studies via the v2 API.

## Endpoint

```
GET /api/studies?search.term=<keyword>
```

### Query Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `search.term` | ✅ | Keyword to search for (e.g. `diabetes`, `cancer vaccine`) |
| `pageSize` | ❌ | Number of results to return (default: `10`, max: `1000`) |
| `pageToken` | ❌ | Token for retrieving the next page of results |

### Example Request

```
GET /api/studies?search.term=diabetes&pageSize=5
```

### Example Response

```json
{
  "searchTerm": "diabetes",
  "totalCount": 42000,
  "nextPageToken": "...",
  "studies": [
    {
      "nctId": "NCT12345678",
      "briefTitle": "A Study of ...",
      "officialTitle": "A Randomized Controlled ...",
      "overallStatus": "RECRUITING",
      "startDate": "2023-01-15",
      "completionDate": "2025-06-30",
      "briefSummary": "This study evaluates ...",
      "conditions": ["Type 2 Diabetes"],
      "centralContacts": [
        {
          "name": "Jane Doe",
          "phone": "555-123-4567",
          "email": "jane.doe@example.com"
        }
      ]
    }
  ]
}
```

## Local Development

### Prerequisites

- Python 3.10+
- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) (local storage emulator)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run locally

```bash
func start
```

## Deployment

Deploy to Azure using the Azure Functions Core Tools:

```bash
az login
func azure functionapp publish <YOUR_FUNCTION_APP_NAME>
```
