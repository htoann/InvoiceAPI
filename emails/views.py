from django.shortcuts import render, redirect
from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
import os
import pathlib
import pickle
import google.oauth2.credentials

# Load OAuth 2.0 Client ID JSON
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Chỉ sử dụng trong phát triển
CLIENT_SECRETS_FILE = os.path.join(pathlib.Path(__file__).parent, 'client_secret.json')

# Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Flow
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri='http://localhost:8000/emails/oauth2callback'
)

def index(request):
    return render(request, 'index.html')

def oauth2_login(request):
    authorization_url, state = flow.authorization_url()
    request.session['state'] = state
    return redirect(authorization_url)

def oauth2_callback(request):
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)
    return redirect('inbox')

def inbox(request):
    if 'credentials' not in request.session:
        return redirect('oauth2_login')

    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials'])

    service = build('gmail', 'v1', credentials=credentials)

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])
        email_data = {header['name']: header['value'] for header in headers}
        emails.append({
            'subject': email_data.get('Subject'),
            'from': email_data.get('From'),
            'date': email_data.get('Date')
        })

    request.session['credentials'] = credentials_to_dict(credentials)
    return render(request, 'inbox.html', {'emails': emails})

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
