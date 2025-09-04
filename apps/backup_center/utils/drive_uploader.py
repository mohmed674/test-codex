# apps/backup_center/utils/drive_uploader.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def _settings_dir() -> Path:
    """Directory to store oauth token/settings."""
    base = Path(settings.BASE_DIR)  # safer than getattr(settings, ...)
    d = base / "credentials"
    d.mkdir(exist_ok=True)
    return d


def _settings_yaml_path() -> Path:
    """
    Location of PyDrive2 settings.yaml.
    Provide client_config_file/client_config_backend/token storage.
    """
    p = _settings_dir() / "pydrive2_settings.yaml"
    if not p.exists():
        # Create a minimal settings template if missing
        p.write_text(
            "\n".join(
                [
                    "client_config_backend: file",
                    "client_config_file: ./credentials/client_secrets.json",
                    "save_credentials: True",
                    "save_credentials_backend: file",
                    "save_credentials_file: ./credentials/token.json",
                    "oauth_scope:",
                    "  - https://www.googleapis.com/auth/drive.file",
                ]
            ),
            encoding="utf-8",
        )
    return p


def _gauth() -> GoogleAuth:
    """Build and authorize GoogleAuth (interactive first time, then cached)."""
    gauth = GoogleAuth(settings_file=str(_settings_yaml_path()))
    # Try load saved creds; if not exist will go through local webserver auth
    gauth.LoadCredentialsFile(str(_settings_dir() / "token.json"))
    if gauth.credentials is None:
        # First-time auth (opens browser once)
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile(str(_settings_dir() / "token.json"))
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile(str(_settings_dir() / "token.json"))
    else:
        gauth.Authorize()
    return gauth


def upload_to_drive(
    file_path: str | os.PathLike[str],
    folder_id: Optional[str] = None,
    mime_type: Optional[str] = None,
) -> str:
    """
    Upload a file to Google Drive. Returns file id.

    Args:
        file_path: local path to file
        folder_id: optional target folder id
        mime_type: optional explicit mime type
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")

    drive = GoogleDrive(_gauth())

    # Use Dict[str, Any] to allow nested lists/dicts (parents, etc.)
    metadata: Dict[str, Any] = {"title": p.name}
    if folder_id:
        # Drive v2 expects a list of parents dicts with "id"
        metadata["parents"] = [{"id": folder_id}]

    f = drive.CreateFile(metadata)
    f.SetContentFile(str(p))
    if mime_type:
        f["mimeType"] = mime_type
    f.Upload()
    return f["id"]
