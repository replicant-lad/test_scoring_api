import requests
import json

class LanguageTestSubmission:
    """
    A class for managing and submitting foreign language writing test responses to the grading API

    Attributes:
        url (str): The API endpoint URL for submission
        language (str): Target language for the test
        submission_response (list): A list of responses with the question, answer, and attached criteria.
        submission_overall_criteria (list): A list of criteria applied to the entirety of the test.
    """


    def __init__(self, url, language):
        """
        Initialize the LanguageTestSubmission object.

        Args:
            url (str): The API Endpoint
            language (str): The target language of the test.
        """
        self.url = url
        self.language = language
        self.submission_responses = []
        self.submission_overall_criteria = []

    def add_overall_criteria(self, criteria):
        """
        Add the overarching criteria to the entire test submission.

        Args:
            criteria (dict): A dictionary of required criteria, such as the name.
        """
        self.submission_overall_criteria.append(criteria)

        return self

    def add_response(self, question, answer, criteria: list):
        """
        Adds a question response to the submission.

        Args:
            question (str): The text of the question.
            answer (str): The test-taker's response.
            criteria (list): A list of dictionary criteria for the individual question.
        """
        self.submission_responses.append({
            "questionText": question,
            "responseText": answer,
            "criteria": criteria
        })
        
        return self
    
    def add_bulk_responses(self, responses):
        """
        Adds multiple responses to the submission

        Args:
            responses (list): A list of dictionaries where each dictionary represents an individual response.
        """
        for response in responses:
            if not all(key in response for key in ["questionText", "responseText", "criteria"]):
                raise ValueError("Each response must include a questionText, reponseText, and criteria field")
        self.submission_responses.append(response)

        return self

    def package_responses(self):
        """
        Packages the submission into a dictionary.

        Returns:
            dict: A dictionary of the submission data, for being converted into a json at API POST.
        """
        return {
            "submission": {
                "targetLanguage": self.language,
                "responses": self.submission_responses,
                "overallCriteria": self.submission_overall_criteria
            }
        }

    def submit_response(self):
        """
        Submit the packaged responses to the API.

        Returns:
            dict: The API responds in JSON format with either the test result or an error code.

        Raises:
            ValueError: If the API returns an error response.
            Exception: Any general errors raised during the request.
        """    
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


submission = (
    LanguageTestSubmission('http://127.0.0.1:5000/v1', "French")
    .add_overall_criteria({"name": "French Test One"})
    .add_response(
        question="Translate: Ceci n'est pas une pipe",
        answer="This is not a pipe.",
        criteria=[{"name": "Grammar"}]
    )
    .add_response(
        question="Translate: This is a test example.",
        answer="Ceci est un exemple de test.",
        criteria=[{"name": "Accuracy"}]
    )
)

response = submission.submit_response()
print(json.dumps(response, indent=4))


"""
Considerations:

    Criteria Changing: The handling of criteria (especially the language) is clunky. Adding more helper methods for updating/removing criteria is
        an obvious next step.

    Data Validation: Right now this wrapper depends entirely on the API responding with error codes for handling submission errors.
        Validating the submission prior to the POST is a good idea - could be done comparing against a schema using the json library.

    Bulk Responses: I added the possibility for adding bulk responses for situations like multiple-questions per page, but did not build
        out an example of this usage.

    Custom Object Response: Right now the wrapper just returns the raw json delivered by the API - instead converting the json into a
        custom object would help limit downstream issues (and repair coding) if the API's response changes structure or extensions are
        needed.

    Error Handling: Lots of room for improvement here - building out exception objects and an error handler instead of returning actual error messages,
        including retries (and a queue in general) for connection failures, and logging all immediately come to mind.

"""