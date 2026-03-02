import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
ADMINS = os.getenv('ADMINS', '')
ADMINS = [int(i) for i in ADMINS.split(',') if i.strip().isdigit()]