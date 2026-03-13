import json
import boto3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

PROFESSORS = [
    {
        "name": "Ravi Adve",
        "department": "Electrical & Computer Engineering",
        "research": "wireless communication, signal processing, distributed beamforming in massive MIMO systems",
        "lab": "Wireless Communication Group",
        "credentials": "Professor, University of Toronto",
        "website": "https://www.comm.utoronto.ca/~rsadve/"
    },
    {
        "name": "Sanja Fidler",
        "department": "Computer Science",
        "research": "computer vision, 3D scene understanding, generative AI, neural rendering, image synthesis",
        "lab": "Vision and Learning Lab",
        "credentials": "Professor, University of Toronto / NVIDIA Research",
        "website": "https://www.cs.toronto.edu/~fidler/"
    },
    {
        "name": "Geoffrey Hinton",
        "department": "Computer Science",
        "research": "deep learning, neural networks, unsupervised learning, capsule networks, AI safety",
        "lab": "Machine Learning Group",
        "credentials": "Professor Emeritus, University of Toronto / Turing Award Laureate",
        "website": "https://www.cs.toronto.edu/~hinton/"
    },
    {
        "name": "Sheila McIlraith",
        "department": "Computer Science",
        "research": "artificial intelligence, automated planning, reward machine learning, knowledge representation",
        "lab": "Knowledge Representation and Reasoning Group",
        "credentials": "Professor, University of Toronto",
        "website": "https://www.cs.toronto.edu/~sheila/"
    },
    {
        "name": "Bo Wang",
        "department": "Computer Science & Medicine",
        "research": "computational biology, single-cell genomics, AI in healthcare, drug discovery, multiomics",
        "lab": "AI in Medicine Lab",
        "credentials": "Assistant Professor, University of Toronto",
        "website": "https://wanglab.ca"
    },
    {
        "name": "Angela Schoellig",
        "department": "Aerospace Engineering",
        "research": "robotics, autonomous systems, machine learning for control, safe reinforcement learning, drones",
        "lab": "Dynamic Systems Lab",
        "credentials": "Professor, University of Toronto",
        "website": "https://www.dynsyslab.org"
    },
    {
        "name": "Raquel Urtasun",
        "department": "Computer Science",
        "research": "self-driving cars, 3D scene understanding, LiDAR perception, autonomous driving safety",
        "lab": "Uber ATG / Machine Learning Group",
        "credentials": "Professor, University of Toronto / Waabi AI Founder",
        "website": "https://www.cs.toronto.edu/~urtasun/"
    },
    {
        "name": "Frank Rudzicz",
        "department": "Computer Science & Medicine",
        "research": "speech processing, NLP for clinical applications, Alzheimer's detection via speech, assistive tech",
        "lab": "Toronto Rehabilitation Institute AI Lab",
        "credentials": "Associate Professor, University of Toronto",
        "website": "https://www.cs.toronto.edu/~frank/"
    },
    {
        "name": "Marzyeh Ghassemi",
        "department": "Computer Science & Medicine",
        "research": "machine learning for health, clinical NLP, bias in AI, ICU prediction models, fair ML",
        "lab": "Health Machine Learning Lab",
        "credentials": "Assistant Professor, University of Toronto",
        "website": "https://healthyml.org"
    },
    {
        "name": "Jonathan Kelly",
        "department": "Aerospace Engineering",
        "research": "state estimation, SLAM, robot perception, probabilistic robotics, sensor fusion",
        "lab": "Space & Terrestrial Autonomous Robotic Systems Lab",
        "credentials": "Associate Professor, University of Toronto",
        "website": "https://stars.utias.utoronto.ca"
    }
]


def call_bedrock(query: str) -> dict:
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    professor_list = json.dumps(PROFESSORS, indent=2)

    prompt = f"""You are an academic research advisor helping undergraduate students find professors to work with.

A student has described their research interests as:
"{query}"

Here is a list of professors and their research areas:
{professor_list}

Your task: Select the TOP 3 professors who best match the student's interests. For each professor, return a JSON object with these exact keys:
- "name": professor's full name (string)
- "lab": their lab name (string)
- "research_explanation": explain their research in 2 simple sentences a high school student could understand (string)
- "match_reason": 1-2 sentences explaining why this professor matches the student's query (string)
- "email_template": a short, warm cold email the student could send to this professor. Use [Student Name] and [Your University] as placeholders. Reference the specific lab and research area. Keep it under 120 words. (string)

Return ONLY a valid JSON object in this exact format, no markdown, no code blocks:
{{
  "matches": [
    {{
      "name": "...",
      "lab": "...",
      "research_explanation": "...",
      "match_reason": "...",
      "email_template": "..."
    }}
  ]
}}"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    })

    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    text = result["content"][0]["text"].strip()

    # Strip markdown code blocks if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    return json.loads(text)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(".", "script.js")


@app.route("/match", methods=["POST"])
def match():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Missing query field"}), 400

    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    try:
        result = call_bedrock(query)
        # Enrich with professor metadata
        prof_map = {p["name"]: p for p in PROFESSORS}
        for match in result.get("matches", []):
            prof = prof_map.get(match["name"], {})
            match["department"] = prof.get("department", "")
            match["credentials"] = prof.get("credentials", "")
            match["website"] = prof.get("website", "#")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)