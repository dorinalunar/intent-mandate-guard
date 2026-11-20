# Contributing to IntentMandateGuard

1. Run the 60-test suite before opening a PR:
   ```bash
   python3 -m pip install -r requirements-dev.txt
   python3 -m pytest -v
   ```
2. Verify snapshot and schema consistency:
   ```bash
   python3 scripts/update_code_snapshot.py verify
   python3 scripts/validate_schemas.py
   ```
3. Build and typecheck the web console:
   ```bash
   cd web && npm install && npm run typecheck && npm run build
   ```
