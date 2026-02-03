"""Compatibility placeholder.

This repository layout includes /server/query-api to match the OVPO TODO/target structure.
For Python importability (hyphens are not valid module names), the runnable FastAPI app lives
at /server/query_api/app.py.

Use:
  uvicorn server.query_api.app:app --port 8081
"""

from server.query_api.app import app  # noqa: F401
