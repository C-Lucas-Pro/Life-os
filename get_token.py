from google_auth_oauthlib.flow import InstalledAppFlow

# On demande la permission de gérer les fichiers
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    # Cela va ouvrir une page web pour te connecter
    creds = flow.run_local_server(port=0)
    
    # On sauvegarde le passeport
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("✅ token.json créé avec succès ! Envoie ce fichier sur ton serveur.")

if __name__ == '__main__':
    main()