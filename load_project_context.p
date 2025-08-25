import os
import json

def load_context():
    path = os.path.join(os.path.dirname(__file__), 'project_meta.json')
    if not os.path.exists(path):
        raise FileNotFoundError("❌ ملف project_meta.json غير موجود. شغّل analyze_project.py أولاً.")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("✅ تم تحميل إعدادات المشروع:")
    print(f"- المجلد الجذر: {data['project_root']}")
    print(f"- إعدادات: {data['settings_module']}")
    print(f"- التطبيقات:")
    for app, model_list in data['apps'].items():
        print(f"  • {app}: {', '.join(model_list)}")
    
    return data
