# Foreign Language Writing Test Scoring API

## Overview
This API provides an endpoint for scoring foreign language writing tests. Each request contains a single test submission with its questions, responses, and scoring criteria.

## Base URL
```
https://api.example.com/v1
```

## Endpoints

### Score Writing Submission
Score a writing submission against provided criteria.

**POST** `/score`

#### Request Body
```json
{
  "submission": {
    "targetLanguage": string,  // (e.g., "Spanish" or "French")
    "responses": [
      {
        "questionText": string,     // The actual question text
        "responseText": string,     // The test-taker's written response
        "criteria": [               // Criteria specific to this question
          {
            "name": string         // e.g., "Grammar", "Mechanics", "Fluidity"
          }
        ]
      }
    ],
    "overallCriteria": [           // Criteria applied to the entire test
      {
        "name": string            // e.g., "Fluency", "Comprehension"
      }
    ]
  }
}
```

#### Response Body
```json
{
  "scores": [
    {
      "criteriaScores": [           // Scores for this question's specific criteria
        {
          "name": string,
          "score": number,
          "feedback": string,
          "confidence": number
        }
      ]
    }
  ],
  "overallCriteriaScores": [        // Scores for test-wide criteria
    {
      "name": string,
      "score": number,
      "feedback": string,
      "confidence": number
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: Invalid submission format or missing required fields
- `422 Unprocessable Entity`: Valid request but submission cannot be scored
- `500 Internal Server Error`: Server-side processing error

## Error Handling
All errors follow consistent format:
```json
{
  "error": {
    "code": string,
    "message": string
  }
}
```

Common error codes:
- `invalid_request`: Malformed request or missing fields
- `invalid_submission`: Submission content issues
- `invalid_rubric`: Rubric format or criteria issues
- `processing_error`: Scoring engine errors
- `internal_error`: Server-side problems
