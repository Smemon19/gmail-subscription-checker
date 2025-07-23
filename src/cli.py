#!/usr/bin/env python3
import argparse
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from parser import parse_subscriptions
from scoring import fetch_senders, score_senders
from fetcher import list_messages

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_PATH = 'token.json'

def get_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('gmail', 'v1', credentials=creds)

def main():
    parser = argparse.ArgumentParser(
        description="Gmail Subscription Checker: list, parse, and score your subscription emails"
    )
    parser.add_argument('-n', '--max-results', type=int, default=20,
                        help='Number of messages to process (default: 20)')
    parser.add_argument('--list', action='store_true',
                        help='List recent messages with basic metadata')
    parser.add_argument('--parse', action='store_true',
                        help='Extract unsubscribe links from subscription emails')
    parser.add_argument('--score', action='store_true',
                        help='Score senders by frequency')

    args = parser.parse_args()

    if args.list:
        list_messages(args.max_results)

    if args.parse:
        parse_subscriptions(args.max_results)

    if args.score:
        senders = fetch_senders(args.max_results)
        if senders:
            score_senders(senders)

    if not any([args.list, args.parse, args.score]):
        print("=== Parsing subscriptions ===")
        parse_subscriptions(args.max_results)
        print("\n=== Scoring senders ===")
        senders = fetch_senders(args.max_results)
        if senders:
            score_senders(senders)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
