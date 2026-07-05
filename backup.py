import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- CONFIGURATION ---
FOLDER_ID = '1YQDvzh6YRlPu636roKO2YqCK81PFWNv_' # <-- Remets bien l'ID de ton dossier Drive ici !
TOKEN_FILE = 'token.json' # Le fichier qu'on vient de générer
FILES_TO_BACKUP = [
    'data/budget.xlsx',
    'data/taches.xlsx',
    'data/voiture.xlsx', 
    'data/suivi.xlsx',
    'data/objectifs.xlsx'
]

def authenticate():
    # On utilise le token.json qui contient ton identité
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/drive.file'])
    return build('drive', 'v3', credentials=creds)

def upload_files():
    try:
        service = authenticate()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"🔄 Sauvegarde du {date_str} avec l'identité de l'utilisateur...")

        for file_path in FILES_TO_BACKUP:
            if os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                target_name = f"BACKUP_{date_str}_{file_name}"
                
                file_metadata = {'name': target_name, 'parents': [FOLDER_ID]}
                media = MediaFileUpload(file_path, resumable=True)
                
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"✅ {target_name} sauvegardé (ID: {file.get('id')})")
            else:
                print(f"⚠️ Fichier manquant : {file_path}")
                
    except Exception as e:
        print(f"❌ Erreur critique : {e}")

if __name__ == '__main__':
    upload_files()