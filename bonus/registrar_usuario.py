import os
import json

def registrar_usuario(user):
    """
    Registra o ID de qualquer usuário que enviar mensagem no usuarios.json.
    Sempre salva o id como chave. Se possível, salva também o nome/username como valor.
    """
    user_id = str(user.id)
    username = None
    if hasattr(user, 'username') and user.username:
        username = user.username
    elif hasattr(user, 'full_name') and user.full_name:
        username = user.full_name
    elif hasattr(user, 'first_name') and user.first_name:
        username = user.first_name
    else:
        username = None
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
    os.makedirs(storage_dir, exist_ok=True)
    usuarios_path = os.path.join(storage_dir, "usuarios.json")
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    # Só registra se ainda não existir no arquivo (não sobrescreve nomes já cadastrados)
    if user_id not in usuarios_map:
        if username:
            usuarios_map[user_id] = username
        else:
            usuarios_map[user_id] = user_id
        with open(usuarios_path, "w", encoding="utf-8") as f:
            json.dump(usuarios_map, f, ensure_ascii=False, indent=4)
