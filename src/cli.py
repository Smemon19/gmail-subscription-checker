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

def interactive_menu(max_results):
    print("\\nChoose an action:")
    print("1) List recent messages")
    print("2) Extract unsubscribe links")
    print("3) Score senders by frequency")
    print("4) Run all tasks")
    print("0) Exit")
    choice = input("Enter choice [0-4]: ").strip()
    if choice == '1':
        list_messages(max_results)
    elif choice == '2':
        parse_subscriptions(max_results)
    elif choice == '3':
        senders = fetch_senders(max_results)
        if senders:
            score_senders(senders)
    elif choice == '4':
        list_messages(max_results)
        print("\\n=== Parsing subscriptions ===")
        parse_subscriptions(max_results)
        print("\\n=== Scoring senders ===")
        senders = fetch_senders(max_results)
        if senders:
            score_senders(senders)
    elif choice == '0':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid choice, please try again.")
        interactive_menu(max_results)

def main():
    parser = argparse.ArgumentParser(
        description="Gmail Subscription Checker CLI"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # common arg
    parser.add_argument('-n', '--max-results', type=int, default=20,
                        help='Number of messages to process (default: 20)')

    # subcommands
    subparsers.add_parser('list', help='List recent messages with metadata')
    subparsers.add_parser('parse', help='Extract unsubscribe links')
    subparsers.add_parser('score', help='Show top senders by frequency')
    subparsers.add_parser('all', help='Run list, parse, and score in sequence')
    subparsers.add_parser('interactive', help='Interactive menu')

    args = parser.parse_args()
    max_results = args.max_results

    if args.command == 'list':
        list_messages(max_results)
    elif args.command == 'parse':
        parse_subscriptions(max_results)
    elif args.command == 'score':
        senders = fetch_senders(max_results)
        if senders:
            score_senders(senders)
    elif args.command == 'all':
        list_messages(max_results)
        print("\\n=== Parsing subscriptions ===")
        parse_subscriptions(max_results)
        print("\\n=== Scoring senders ===")
        senders = fetch_senders(max_results)
        if senders:
            score_senders(senders)
    else:
        interactive_menu(max_results)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
