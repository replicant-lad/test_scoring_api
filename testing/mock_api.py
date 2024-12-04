import json
from flask import Flask, jsonify, request
from jsonschema import validate, ValidationError

app = Flask(__name__)

@app.route('/v1/score', methods=['POST'])
def score_submission():
    try:
        # Verify the incoming submission meets requirements.
        data = request.get_json(force=True, silent=True)

        if data is None:
            return error_response("invalid_request", "The request is not valid JSON", 400)

        error = verify_submission(data)
        if error:
            return error

        # Check scores against rubric - leaving a hard-coded copy in here but there's an easy solution for tying a test id or the criteria naming
        # to a rubric json hosted on a server. Just going to use Correct/Incorrect for grading simplicity.
        mock_rubric = {
            "testAnswers": [
                {
                    "questionName": "Question1",
                    "questionText": "Translate: Ceci n'est pas une pipe",
                    "questionAnswer": "This is not a pipe."
                },
                {
                    "questionName": "Question2",
                    "questionText": "Translate: This is a test example.",
                    "questionAnswer": "Ceci est un exemple de test."
                }
            ]
        }

        response_body = {
            "scores": [],
            "overallCriteriaScores": []
        }

        total_score = 0
        total_confidence = 0
        total_questions = len(data["submission"]["responses"])
        all_correct = True

        for response in data["submission"]["responses"]:
            # Match the question in the rubric
            matched_question = next(
                (q for q in mock_rubric["testAnswers"] if q["questionText"] == response["questionText"]),
                None
            )

            if matched_question:
                # Compare the response
                score = 1 if matched_question["questionAnswer"] == response["responseText"] else 0
                feedback = "Correct" if score == 1 else "Incorrect"
                confidence = 1 if score == 1 else 0

                if score == 0:
                    all_correct = False

                total_score += score
                total_confidence += confidence

                response_body["scores"].append({
                    "criteriaScores": [
                        {
                            "name": response["criteria"][0]["name"],
                            "score": score,
                            "feedback": feedback,
                            "confidence": confidence
                        }
                    ]
                })
            else:
                return error_response("invalid_rubric", "Questions do not match accessed rubric", 422)

        response_body["overallCriteriaScores"].append({
            "name": data["submission"]["overallCriteria"][0]["name"],
            "score": total_score,
            "feedback": "Perfect" if all_correct else "Almost",
            "confidence": total_confidence / total_questions
        })

        # Quick note, jsonify doesn't guarantee an order when serializing so there's good odds it will return the overall Criteria scores first.
        # Could work around this using an OrderedDict, but ultimately the order of the json shouldn't be relevant.

        return jsonify(response_body)

    except Exception as e:
        return error_response("internal_error", str(e), 500)

def load_schema(schema_path="./schema.json"):
    with open(schema_path, "r") as schema_file:
        return json.load(schema_file)

def verify_submission(data):
    try:
        
        expected_schema = load_schema()

        validate(instance=data, schema=expected_schema)
        return None

    except ValidationError as e:
        return error_response("invalid_request", f"Invalid data structure: {e.message}", 400)

def error_response(error_code, error_message, status_code):
    return jsonify({"error": {"code": error_code, "message": error_message}}), status_code

if __name__ == '__main__':
    app.run(port=5000, debug=True)
