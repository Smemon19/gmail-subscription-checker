import os
import re
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
# Point TOKEN_FILE at the project-root token.json
TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'token.json'))

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def decode_body(data):
    decoded = base64.urlsafe_b64decode(data.encode('ASCII'))
    return decoded.decode('utf-8', errors='replace')

def extract_unsubscribe_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text().lower()
        if 'unsubscribe' in href or 'unsubscribe' in text:
            links.append(href)
    return list(set(links))

def parse_subscriptions_data(max_results=10):
    service = get_service()
    resp = service.users().messages().list(userId='me', maxResults=max_results).execute()
    msgs = resp.get('messages', [])
    data = []

    for m in msgs:
        full = service.users().messages().get(
            userId='me',
            id=m['id'],
            format='full'
        ).execute()
        headers = {h['name']: h['value'] for h in full['payload']['headers']}
        subject = headers.get('Subject', '(no subject)')
        unsub_links = []

        # 1) List-Unsubscribe header
        lu = headers.get('List-Unsubscribe', '')
        unsub_links += re.findall(r'<(https?://[^>]+)>', lu)

        # 2) HTML body
        def walk(parts):
            nonlocal unsub_links
            for p in parts or []:
                if p.get('mimeType') == 'text/html' and p.get('body', {}).get('data'):
                    html = decode_body(p['body']['data'])
                    unsub_links += extract_unsubscribe_links(html)
                elif p.get('parts'):
                    walk(p['parts'])
        walk(full['payload'].get('parts'))

        data.append({
            'id': m['id'],
            'subject': subject,
            'unsubscribe_links': list(set(unsub_links))
        })

    return data

# backward-compatible, print-based wrapper
def parse_subscriptions(max_results=10):
    items = parse_subscriptions_data(max_results)
    for item in items:
        if item['unsubscribe_links']:
            print(f"ID: {item['id']}\nSubject: {item['subject']}")
            for link in item['unsubscribe_links']:
                print("  ↳", link)
