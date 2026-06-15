# Permission enforcement hardening plan

- [x] Inspect current permission decorators/usages across backend routes

- [x] Remove duplicate/local permission helper definitions from `backend/app.py`

- [x] Fix `User.to_dict(include_permissions=True)` early-return/unreachable code in `backend/models.py`

- [x] Ensure all route modules import `require_permission` from `backend/permission_service.py`

- [ ] Add missing `@require_permission(...)` decorators to upload/admin endpoints that currently only use `@login_required`
- [ ] Audit resources/actions strings vs `ROLE_PERMISSIONS` to ensure consistency
- [ ] Add a single enforcement decorator/middleware entrypoint (base decorator) for consistent checks
- [ ] Create and run a verification script to confirm enforcement matches DB/role rules

