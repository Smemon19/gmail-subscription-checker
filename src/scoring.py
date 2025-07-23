import collections
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# How many messages to sample (you can adjust this)
SAMPLE_SIZE = 100

def get_service():
    """Load OAuth credentials and build the Gmail API client."""
    creds = Credentials.from_authorized_user_file('token.json')
    return build('gmail', 'v1', credentials=creds)

def fetch_senders(max_results=SAMPLE_SIZE):
    """
    Fetch up to max_results messages and return a list of sender email addresses.
    """
    service = get_service()
    senders = []
    # 1) List messages
    resp = service.users().messages().list(userId='me', maxResults=max_results).execute()
    msgs = resp.get('messages', [])
    if not msgs:
        print("No messages found.")
        return senders

    # 2) For each message, fetch headers and pull the 'From' field
    for m in msgs:
        msg = service.users().messages().get(
            userId='me',
            id=m['id'],
            format='metadata',
            metadataHeaders=['From']
        ).execute()
        hdrs = {h['name']: h['value'] for h in msg['payload']['headers']}
        full_from = hdrs.get('From', '')
        # Extract just the email address (inside <> if present)
        if '<' in full_from and '>' in full_from:
            email = full_from.split('<')[-1].split('>')[0].strip()
        else:
            email = full_from.strip()
        senders.append(email.lower())
    return senders

def score_senders(senders):
    """
    Count occurrences of each sender, sort descending, and print top results.
    """
    counts = collections.Counter(senders)
    print(f"{'Sender':<40}Count")
    print("-"*50)
    for email, count in counts.most_common(10):
        print(f"{email:<40}{count}")
    print(f"\n(Showing top 10 of {len(counts)} unique senders)")
    print("You can adjust SAMPLE_SIZE at the top of this script.")

if __name__ == '__main__':
    senders = fetch_senders()
    if senders:
        score_senders(senders)
