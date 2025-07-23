import os
import re
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from bs4 import BeautifulSoup

# Match what auth.py used
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

def decode_body(data):
    """Base64-url decode Gmail message bodies to a UTF-8 string."""
    decoded_bytes = base64.urlsafe_b64decode(data.encode('ASCII'))
    return decoded_bytes.decode('utf-8', errors='replace')

def extract_unsubscribe_links(html):
    """Return all links where text or href contains 'unsubscribe'."""
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        text = a.get_text().lower()
        href = a['href']
        if 'unsubscribe' in text or 'unsubscribe' in href:
            links.append(href)
    return list(set(links))  # dedupe

def parse_subscriptions(max_results=10):
    service = get_service()
    # 1) List message IDs
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No messages found.")
        return

    # 2) For each message, fetch full data
    for m in messages:
        msg = service.users().messages().get(
            userId='me',
            id=m['id'],
            format='full'
        ).execute()
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        subject = headers.get('Subject', '(no subject)')
        list_unsub = headers.get('List-Unsubscribe', '')

        # 3) Extract from header if present
        unsub_links = re.findall(r'<(https?://[^>]+)>', list_unsub)

        # 4) Find HTML body
        html = None
        def walk(parts):
            nonlocal html
            for part in parts or []:
                if part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                    html = decode_body(part['body']['data'])
                    return True
                if part.get('parts'):
                    if walk(part['parts']):
                        return True
            return False

        walk(msg['payload'].get('parts'))

        # 5) Parse HTML for unsubscribe links
        if html:
            unsub_links += extract_unsubscribe_links(html)

        # 6) If we found any, print them
        unsub_links = list(set(unsub_links))
        if unsub_links:
            print(f"\nID: {m['id']}\nSubject: {subject}")
            for link in unsub_links:
                print("  ↳", link)

if __name__ == '__main__':
    parse_subscriptions()

