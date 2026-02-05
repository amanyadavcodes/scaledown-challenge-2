import json, uuid, os, datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="")

# --- CONFIGURATION ---
ADMIN_PASSWORD = "admin123" 
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")

if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

RESPONSE_HISTORY = []

def _persist_history():
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(RESPONSE_HISTORY, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def _load_history():
    global RESPONSE_HISTORY
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                RESPONSE_HISTORY = json.load(f)
        except: RESPONSE_HISTORY = []

# --- SURVEY DEFINITION ---
SURVEY_MODULES = [
    {"id": "name", "type": "text", "bot": "Please enter your full name.", "key": "full_name"},
    {"id": "email", "type": "text", "bot": "Please provide your email address.", "key": "email"},
    {"id": "phone", "type": "text", "bot": "Please provide your contact number.", "key": "phone_number"},
    {"id": "category", "type": "multi", "bot": "How can I assist you today?", "options": ["Give Feedback", "Register Complaint"], "key": "category"},
    {"id": "usage", "type": "multi", "bot": "Select use case:", "options": ["Professional", "Educational", "Personal"], "key": "usage"},
    {"id": "frequency", "type": "multi", "bot": "How often do you interact with us?", "options": ["Daily", "Weekly", "Rarely"], "key": "frequency", "show_if": "Feedback"},
    {"id": "satisfaction", "type": "rating", "bot": "Satisfaction level (1-5)?", "key": "satisfaction", "show_if": "Feedback"},
    {"id": "performance", "type": "rating", "bot": "System performance (1-5)?", "key": "performance_score", "show_if": "Feedback"},
    {"id": "recommend", "type": "rating", "bot": "Recommend likelihood (1-5)?", "key": "recommendation_score", "show_if": "Feedback"},
    {"id": "comments", "type": "text", "bot": "Primary factor behind your rating?", "key": "comments", "show_if": "Feedback"},
    {"id": "comp_details", "type": "text", "bot": "Describe your complaint in detail.", "key": "complaint_text", "show_if": "Complaint"},
    {"id": "outro", "type": "outro", "bot": "Data synchronized. Thank you."}
]

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/next", methods=["POST"])
def get_next_module():
    body = request.get_json(force=True)
    idx = body.get("current_index", -1) + 1
    responses = body.get("responses", {})
    if idx >= len(SURVEY_MODULES): return jsonify({"done": True})
    module = SURVEY_MODULES[idx]
    category = responses.get("category", "")
    if "show_if" in module and module["show_if"] not in category:
        return get_next_module_recursive(idx, responses)
    return jsonify({"done": False, "index": idx, "module": module})

def get_next_module_recursive(idx, responses):
    next_idx = idx + 1
    if next_idx >= len(SURVEY_MODULES): return jsonify({"done": True})
    module = SURVEY_MODULES[next_idx]
    category = responses.get("category", "")
    if "show_if" in module and module["show_if"] not in category:
        return get_next_module_recursive(next_idx, responses)
    return jsonify({"done": False, "index": next_idx, "module": module})

@app.route("/api/submit", methods=["POST"])
def submit_response():
    body = request.get_json(force=True)
    _load_history()
    res = body.get("responses", {})
    is_complaint = "Complaint" in res.get("category", "")
    u_no = len(RESPONSE_HISTORY) + 1
    t_id = f"{'CMP' if is_complaint else 'FBK'}-{u_no:03d}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    record = {
        "no": u_no, "ticket_id": t_id, "timestamp": timestamp,
        "category": "Complaint" if is_complaint else "Feedback",
        "status": "Pending" if is_complaint else "Closed",
        "responses": res, "report_file": f"{t_id}.txt"
    }
    RESPONSE_HISTORY.append(record)
    _persist_history()
    file_path = os.path.join(REPORTS_DIR, f"{t_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"TICKET ID: {t_id}\nDATE: {timestamp}\n" + "="*40 + "\n\n")
        for k, v in res.items(): f.write(f"{k.upper():<20}: {v}\n")
    return jsonify({"status": "ok", "ticket_id": t_id, "category": record['category']})

@app.route("/api/track", methods=["POST"])
def track():
    body = request.get_json(force=True)
    _load_history()
    t_id = body.get("ticket_id", "").strip().upper()
    match = next((r for r in RESPONSE_HISTORY if r.get('ticket_id') == t_id), None)
    if match:
        return jsonify({"found": True, "status": match.get('status', 'Closed'), "is_feedback": match.get('category') == "Feedback"})
    return jsonify({"found": False})

@app.route("/api/admin/data", methods=["POST"])
def get_data():
    body = request.get_json(force=True)
    if body.get("password") != ADMIN_PASSWORD: return jsonify({"error": "Unauthorized"}), 401
    _load_history()
    return jsonify({"history": RESPONSE_HISTORY})

@app.route("/api/admin/delete", methods=["POST"])
def delete_item():
    body = request.get_json(force=True)
    if body.get("password") != ADMIN_PASSWORD: return jsonify({"error": "Unauthorized"}), 401
    _load_history()
    global RESPONSE_HISTORY
    t_id = body.get("ticket_id")
    record = next((r for r in RESPONSE_HISTORY if r.get('ticket_id') == t_id), None)
    if record:
        file_path = os.path.join(REPORTS_DIR, record.get('report_file', ''))
        if os.path.exists(file_path): 
            try: os.remove(file_path)
            except: pass
        RESPONSE_HISTORY = [r for r in RESPONSE_HISTORY if r.get('ticket_id') != t_id]
        _persist_history()
        return jsonify({"status": "ok"})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/admin/resolve", methods=["POST"])
def resolve():
    body = request.get_json(force=True)
    if body.get("password") != ADMIN_PASSWORD: return jsonify({"error": "Unauthorized"}), 401
    _load_history()
    t_id = body.get("ticket_id")
    for r in RESPONSE_HISTORY:
        if r.get('ticket_id') == t_id:
            r['status'] = "Resolved"
            _persist_history()
            return jsonify({"status": "ok"})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/admin/view/<filename>")
def view_txt(filename):
    return send_from_directory(REPORTS_DIR, filename)

if __name__ == "__main__":
    _load_history()
    app.run(debug=True, port=5000)