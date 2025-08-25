import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
META_PATH = os.path.join(BASE_DIR, 'project_meta.json')
STATE_PATH = os.path.join(BASE_DIR, 'project_state.json')

def load_context():
    if not os.path.exists(META_PATH):
        raise FileNotFoundError("❌ ملف project_meta.json غير موجود.")
    if not os.path.exists(STATE_PATH):
        # ملف الحالة غير موجود، نرجع حالة افتراضية
        return json.load(open(META_PATH, encoding='utf-8')), {
            "last_script": None,
            "next_script": None,
            "status": "initial",
            "last_updated": None
        }

    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    with open(STATE_PATH, 'r', encoding='utf-8') as f:
        state = json.load(f)

    return meta, state
