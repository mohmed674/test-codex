import os
import sys
import django
from django.db import connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM plm_productlifecycle;")
    count = cursor.fetchone()[0]

    if count == 0:
        print("✅ الجدول plm_productlifecycle فارغ. لا حاجة للحذف.")
    else:
        print(f"⚠️ الجدول يحتوي على {count} صف. سيتم حذفها...")
        cursor.execute("DELETE FROM plm_productlifecycle;")
        print("✅ تم الحذف بنجاح.")
