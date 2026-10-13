from werkzeug.security import generate_password_hash

# Synthetic accounts for local-only testing.
# Passwords are hashed before being stored.
USERS = {
    "alice": {
        "id": "alice",
        "username": "alice",
        "role": "user",
        "password_hash": generate_password_hash("Secret123!"),
    },
    "bob": {
        "id": "bob",
        "username": "bob",
        "role": "user",
        "password_hash": generate_password_hash("Secret123!"),
    },
    "admin": {
        "id": "admin",
        "username": "admin",
        "role": "admin",
        "password_hash": generate_password_hash("AdminPass456!"),
    },
}

# Synthetic private records for authorization testing.
RECORDS = {
    "A1": {
        "id": "A1",
        "owner": "alice",
        "title": "Alice's Note 1",
        "content": "Synthetic private content for record A1.",
    },
    "A2": {
        "id": "A2",
        "owner": "alice",
        "title": "Alice's Note 2",
        "content": "Synthetic private content for record A2.",
    },
    "B1": {
        "id": "B1",
        "owner": "bob",
        "title": "Bob's Note 1",
        "content": "Synthetic private content for record B1.",
    },
    "B2": {
        "id": "B2",
        "owner": "bob",
        "title": "Bob's Note 2",
        "content": "Synthetic private content for record B2.",
    },
}
