# TODO - Copilot project fix

## 1) Dependency compatibility (Python 3.14)
- [x] Identified backend crash cause: Werkzeug/Flask 2.x with Python 3.14.
- [x] Update `backend/requirements.txt` to Flask 3.x / Werkzeug 3.x.
- [x] Reinstall backend dependencies in `.venv`.
- [x] Verify backend starts (`python backend/app.py`).


## 2) Runtime API fixes
- [ ] Investigate 405 errors like `DELETE /api/admin/blog/undefined`.

## 3) Clean up earlier code shims
- [ ] Ensure no broken compatibility shims remain in `backend/app.py`.

## 4) Frontend wiring
- [ ] Wire Contact + Newsletter backend endpoints (if missing).

## 5) Smoke tests
- [ ] Verify: `/api/products`, `/api/blog`, `/api/blog/<slug>`, admin endpoints.

