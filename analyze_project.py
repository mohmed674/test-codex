import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
apps = []
models = {}

def is_django_app(path):
    return (
        os.path.isdir(path)
        and os.path.isfile(os.path.join(path, 'models.py'))
        and os.path.isfile(os.path.join(path, 'apps.py'))
    )

for item in os.listdir(BASE_DIR):
    full_path = os.path.join(BASE_DIR, item)
    if is_django_app(full_path):
        apps.append(item)
        with open(os.path.join(full_path, 'models.py'), 'r', encoding='utf-8') as f:
            content = f.read()
            declared = []
            for line in content.splitlines():
                line = line.strip()
                if line.startswith('class ') and '(models.Model)' in line:
                    declared.append(line.split('class ')[1].split('(')[0].strip())
            if declared:
                models[item] = declared

project_meta = {
    "project_root": BASE_DIR,
    "settings_module": "config.settings",
    "apps": models,
    "scripts_folder": BASE_DIR,
    "last_script": None
}

with open(os.path.join(BASE_DIR, 'project_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(project_meta, f, indent=2, ensure_ascii=False)

print("✅ تم إنشاء ملف project_meta.json بنجاح.")
