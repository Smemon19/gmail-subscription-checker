from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def list_messages(n=10):
    # Load credentials from token.json
    creds = Credentials.from_authorized_user_file('token.json')
    # Build the Gmail API client
    service = build('gmail', 'v1', credentials=creds)

    # Fetch a list of message IDs
    results = service.users().messages().list(
        userId='me',
        maxResults=n
    ).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        return

    # For each message ID, fetch metadata and print
    for m in messages:
        msg = service.users().messages().get(
            userId='me',
            id=m['id'],
            format='metadata',
            metadataHeaders=['Date', 'From', 'Subject']
        ).execute()
        headers = { h['name']: h['value'] for h in msg['payload']['headers'] }
        date = headers.get('Date', 'N/A')
        sender = headers.get('From', 'N/A')
        subject = headers.get('Subject', 'N/A')
        print(f"{date} | {sender} | {subject}")

if __name__ == '__main__':
    list_messages()

