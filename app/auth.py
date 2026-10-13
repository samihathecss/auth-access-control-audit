from functools import wraps

from flask_wtf.csrf import generate_csrf

from flask import Blueprint, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from app.models import USERS

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    """Require an authenticated user."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view



def admin_required(view):
    """Require an authenticated administrator."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))

        user = next(
            (
                u for u in USERS.values()
                if u["id"] == session.get("user_id")
            ),
            None,
        )

        if user is None or user["role"] != "admin":
            session.clear()
            return jsonify({"error": "Forbidden"}), 403

        return view(*args, **kwargs)

    return wrapped_view



@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return jsonify({
            "message": "Submit username and password to log in.",
		  "csrf_token": generate_csrf(),
        })

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = request.form

    username = data.get("username", "")
    password = data.get("password", "")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid username or password"}), 401

    user = USERS.get(username)

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Clear any existing session values before establishing a new login.
    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]

    return jsonify({
        "message": "Login successful",
        "user": {
            "username": user["username"],
            "role": user["role"],
        },
    })


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"})
