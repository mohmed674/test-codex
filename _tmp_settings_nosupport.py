from config.settings import *
INSTALLED_APPS = [a for a in INSTALLED_APPS if a != "apps.support"]
