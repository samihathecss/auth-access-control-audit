from flask import Blueprint, jsonify
from app.auth import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["GET"])
@admin_required
def admin_dashboard():
    return jsonify({
        "message": "Administrator access granted",
        "section": "admin",
    })
