from flask import Blueprint, jsonify, request, session

from app.auth import login_required
from app.models import RECORDS

records_bp = Blueprint("records", __name__)


@records_bp.route("/records", methods=["GET"])
@login_required
def list_records():
    user_id = session["user_id"]

    owned_records = [
        {
            "id": record["id"],
            "title": record["title"],
        }
        for record in RECORDS.values()
        if record["owner"] == user_id
    ]

    return jsonify({"records": owned_records})


@records_bp.route("/records/<record_id>", methods=["GET"])
@login_required
def get_record(record_id):
    record = RECORDS.get(record_id)

# Return the same response for missing and unauthorized records.
    if record is None or record["owner"] != session["user_id"]:
        return jsonify({"error": "Record not found"}), 404

    return jsonify({
        "id": record["id"],
        "title": record["title"],
        "content": record["content"],
    })


@records_bp.route("/records", methods=["POST"])
@login_required
def create_record():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    content = data.get("content", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(content, str):
        content = ""

    title = title.strip()
    content = content.strip()

    # Generate a new record ID
    new_id = f"R{len(RECORDS) + 1}"
    while new_id in RECORDS:
        new_id = f"R{len(RECORDS) + 2}"

    record = {
        "id": new_id,
        "owner": session["user_id"],
        "title": title,
        "content": content,
    }
    RECORDS[new_id] = record

    return jsonify({
        "id": record["id"],
        "title": record["title"],
        "content": record["content"],
    }), 201


@records_bp.route("/records/<record_id>", methods=["PUT"])
@login_required
def update_record(record_id):
    record = RECORDS.get(record_id)

    if record is None or record["owner"] != session["user_id"]:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON"}), 400

    title = data.get("title")
    content = data.get("content", "")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(content, str):
        content = ""

    record["title"] = title.strip()
    record["content"] = content.strip()

    return jsonify({
        "id": record["id"],
        "title": record["title"],
        "content": record["content"],
    })


@records_bp.route("/records/<record_id>", methods=["DELETE"])
@login_required
def delete_record(record_id):
    record = RECORDS.get(record_id)

    if record is None or record["owner"] != session["user_id"]:
        return jsonify({"error": "Record not found"}), 404

    del RECORDS[record_id]
    return jsonify({"message": "Record deleted"})
