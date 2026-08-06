# WeightTracker REST API (CS 499 Enhancement Three: Databases)

Replaces the app's local SQLite storage with a MongoDB backend exposed
through a Flask REST API. Handles registration/login, per-user weight
entries, and goal-weight tracking, with JWT-based authentication.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (or export environment variables directly):

```
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/weighttracker
JWT_SECRET_KEY=<a long random string>
```

Run the server:

```bash
python app.py
```

By default it listens in `0.0.0.0:5000`. 
From the Android Emulator, reach it at **http://10.0.2.2:5000/**. 
From a physical device on the same Wi-Fi network, use your machine's LAN IP instead.

## Endpoints

| Method | Path               | Auth | Body                   | Notes                                |
|--------|--------------------|------|------------------------|--------------------------------------|
| POST   | /api/register      | no   | `{username, password}` | 409 if username taken                |
| POST   | /api/login         | no   | `{username, password}` | Returns `{token}`                    |
| GET    | /api/entries       | yes  | N/A                    | Returns entries for the current user |
| POST   | /api/entries       | yes  | `{date, weight}`       | date = MM/DD/YYYY                    |
| PUT    | /api/entries/<id>  | yes  | `{date, weight}`       | Only affects the caller's own entry  |
| DELETE | /api/entries/<id>  | yes  | N/A                    | Only affects the caller's own entry  |
| GET    | /api/goal          | yes  | N/A                    | Returns `{goalWeight}`               |
| PUT    | /api/goal          | yes  | `{goalWeight}`         | Sets the caller's goal weight        |

Add the JWT to authenticated requests as:
`Authorization: Bearer <token>`

## Security Notes (What changed vs. the original SQLite version)
- Passwords are hashed with `werkzeug.security.generate_password_hash` 
(salted PBKDF2) instead of stored as plain text.
- All weight-entry and goal routes required a valid JWT and are scoped 
to `get_jwt_identity()`; one user can never read, edit, or delete another user user's data,
even by guessing an entry id (a bug that existed in the original SQLite version, 
where `weight-entries` had no per-user column at all).
- All inputs are type- and format-validated server-side before touching the database, 
which also blocks NoSQL-injection-style payloads (e.g. passing `{"$ne": null}` 
instead of a string for `username`).
- `users.username` has a unique index enforced at the database level, 
and `weight_entries.username` is indexed for fast per-user lookups.
- Error handlers avoid leaking stack traces to the client.

## Production notes

This is configured for local/dev use (`debug=True`, HTTP). 
For a real deployment, you would run behind a WSGI server (gunicorn), 
terminate TLS so all traffic is HTTPS, 
and move `JWT_SECRET_KEY`/`MONGO_URI` into a secrets manager rather than plain environment variables.