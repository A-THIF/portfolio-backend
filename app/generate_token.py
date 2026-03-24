import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

flow = InstalledAppFlow.from_client_secrets_file(
    'app/credentials/oauth_client.json',
    SCOPES
)

creds = flow.run_local_server(port=0)

print("\n===== COPY THIS REFRESH TOKEN =====\n")
print(creds.refresh_token)