from celery import shared_task
import subprocess

@shared_task
def run_inventory_ai_analysis():
    subprocess.run(["python", "manage.py", "ai_inventory_analysis"])
