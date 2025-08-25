from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def upload_to_drive(filepath):
    """
    ✅ يرفع الملف المحدد إلى Google Drive باستخدام PyDrive
    - filepath: المسار الكامل للملف المراد رفعه
    """
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # يتم التفويض عبر المتصفح أول مرة فقط

    drive = GoogleDrive(gauth)
    filename = os.path.basename(filepath)

    file_drive = drive.CreateFile({'title': filename})
    file_drive.SetContentFile(filepath)
    file_drive.Upload()

    return f"Uploaded {filename} to Google Drive"
