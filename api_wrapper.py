import requests
import json

class LanguageTestSubmission:
    def __init__(self, url, language):
        self.url = url
        self.language = language
        self.submission_responses = []
        self.submission_overall_criteria = []

    def add_overall_criteria(self, criteria):
        # Adds an overall criteria to the submission
        self.submission_overall_criteria.append(criteria)

    def add_response(self, question, answer, criteria: list):
        # Adds a response with associated criteria to the submission
        self.submission_responses.append({
            "questionText": question,
            "responseText": answer,
            "criteria": criteria
        })

    def package_responses(self):
        return {
            "submission": {
                "targetLanguage": self.language,
                "responses": self.submission_responses,
                "overallCriteria": self.submission_overall_criteria
            }
        }

    def submit_response(self):
        endpoint = f"{self.url}/score"
        data = self.package_responses()

        try:
            response = requests.post(endpoint, json=data)

            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json().get("error", {})
                error_code = error_data.get("code", "unknown_error")
                error_message = error_data.get("message", "No specific error message provided.")
                raise ValueError(f"API Error: {error_code} - {error_message}")

        except Exception as e:
            raise e


# Example


submission = LanguageTestSubmission('http://127.0.0.1:5000/v1', "French")

# Add the overall criteria
submission.add_overall_criteria({
    "name": "French Test One"
}
)

# Add responses with criteria
submission.add_response(
    question="Translate: Ceci n'est pas une pipe",
    answer="This is not a pipe.",
    criteria=[{"name": "Grammar"}]
)

submission.add_response(
    question="Translate: This is a test example.",
    answer="Ceci est un exemple de test.",
    criteria=[{"name": "Accuracy"}]
)

# Submit responses
try:
    api_response = submission.submit_response()
    print(json.dumps(api_response))
except Exception as e:
    print(f"Error: {e}")
