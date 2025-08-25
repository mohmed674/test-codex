import os
import sys
import django
from django.db import connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

with connection.cursor() as cursor:
    print("⏳ فحص جدول plm_productlifecycle ...")
    cursor.execute("SELECT COUNT(*) FROM plm_productlifecycle;")
    count = cursor.fetchone()[0]

    if count == 0:
        print("✅ الجدول فارغ. لا حاجة للحذف.")
    else:
        print(f"⚠️ يوجد {count} صف في الجدول. جاري الحذف...")
        cursor.execute("DELETE FROM plm_productlifecycle;")
        print("✅ تم الحذف بنجاح.")
