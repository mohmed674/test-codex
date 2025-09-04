import subprocess

from celery import shared_task


@shared_task
def run_inventory_ai_analysis():
    subprocess.run(["python", "manage.py", "ai_inventory_analysis"])
