"""Django's command-line utility for administrative tasks."""
import os
import sys

# ✅ استيراد dotenv فقط إن وُجدت
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv غير متوفرة؟ تجاهل بدون كسر التطبيق

def main():
    print("==== MAIN STARTED ====")

    # ✅ تحديد إعدادات Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__ == '__main__':
    main()
