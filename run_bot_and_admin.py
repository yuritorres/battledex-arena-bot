import subprocess
import sys
import os

# Caminhos dos scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_PATH = os.path.join(BASE_DIR, 'main.py')
ADMIN_GUI_PATH = os.path.join(BASE_DIR, 'admin_gui', 'main.py')
# VENV_PYTHON = os.path.join(BASE_DIR, '.venv', 'Scripts', 'python.exe')
# python_exec = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
python_exec = sys.executable

# Rodar o painel admin no mesmo terminal (em background)
subprocess.Popen([python_exec, ADMIN_GUI_PATH])

# Abrir o painel admin em uma nova janela
#subprocess.Popen([python_exec, ADMIN_GUI_PATH], creationflags=subprocess.CREATE_NEW_CONSOLE)

# Rodar o bot no terminal atual
subprocess.call([python_exec, BOT_PATH])
