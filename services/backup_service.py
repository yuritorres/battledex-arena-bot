import os
from datetime import datetime
from typing import List, Tuple
import zipfile


BACKUP_PREFIX = "battledex-backup"
BACKUP_EXTENSION = ".zip"


def _normalize_path(path: str) -> str:
    return os.path.abspath(os.path.normpath(path))


def _ensure_backups_dir(backups_dir: str) -> str:
    normalized = _normalize_path(backups_dir)
    os.makedirs(normalized, exist_ok=True)
    return normalized


def create_backup_archive(storage_dir: str, backups_dir: str) -> Tuple[str, str]:
    """Create a compressed archive with the current contents of storage_dir.

    Returns a tuple with (absolute archive path, archive file name).
    """
    storage_dir = _normalize_path(storage_dir)
    backups_dir = _ensure_backups_dir(backups_dir)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{BACKUP_PREFIX}-{timestamp}{BACKUP_EXTENSION}"
    archive_path = os.path.join(backups_dir, filename)

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root, dirs, files in os.walk(storage_dir):
            # Skip the backups directory itself to avoid recursive backups
            dirs[:] = [
                d for d in dirs if _normalize_path(os.path.join(root, d)) != backups_dir
            ]
            for file_name in files:
                file_path = os.path.join(root, file_name)
                arcname = os.path.relpath(file_path, storage_dir)
                archive.write(file_path, arcname)

    return archive_path, filename


def restore_backup_archive(storage_dir: str, backups_dir: str, backup_name: str) -> str:
    """Restore storage_dir contents from the given backup archive name."""
    storage_dir = _normalize_path(storage_dir)
    backups_dir = _ensure_backups_dir(backups_dir)

    requested_path = _normalize_path(os.path.join(backups_dir, backup_name))
    if not requested_path.startswith(backups_dir):
        raise ValueError("Nome de backup inválido.")
    if not os.path.exists(requested_path):
        raise FileNotFoundError(f"Backup não encontrado: {backup_name}")

    os.makedirs(storage_dir, exist_ok=True)
    with zipfile.ZipFile(requested_path, "r") as archive:
        archive.extractall(storage_dir)

    return requested_path


def list_available_backups(backups_dir: str) -> List[str]:
    backups_dir = _ensure_backups_dir(backups_dir)
    if not os.path.isdir(backups_dir):
        return []
    return sorted(
        [
            entry
            for entry in os.listdir(backups_dir)
            if entry.endswith(BACKUP_EXTENSION)
        ],
        reverse=True,
    )
