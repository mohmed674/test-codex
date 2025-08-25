import json, datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
inv = json.loads((BASE/"project_inventory.json").read_text(encoding="utf-8"))
state_p = BASE/"project_state.json"
state = json.loads(state_p.read_text(encoding="utf-8")) if state_p.exists() else {}

bundle = {
  "resume_token": "ERP-RESUME",
  "project_root": inv.get("project_root"),
  "settings_module": inv.get("settings_module"),
  "scanned_at": inv.get("scanned_at"),
  "last_updated": state.get("last_updated"),
  "last_script": state.get("last_script"),
  "urls_mode": "minimal_core_only",   # بعد Reset
  "apps_count": len(inv.get("apps", {})),
  "core_models": inv.get("apps", {}).get("core", {}).get("models", []),
  "missing_admin": inv.get("missing_admin", []),
  "next_plan": [
    "re-add apps urls gradually in small batches",
    "verify no duplicate namespaces after each batch"
  ],
  "ts": datetime.datetime.utcnow().isoformat()
}

out = BASE/"resume_bundle.json"
out.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ resume_bundle.json written.")
