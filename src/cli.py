#!/usr/bin/env python3
import argparse, sys, json, csv
from fetcher import list_messages
from parser import parse_subscriptions_data
from scoring import fetch_senders, score_senders
from actions import bulk_unsubscribe

def interactive_menu(n):
    # ... (you can keep your existing menu, plus options 4=unsubscribe,5=export)
    pass  # omitted for brevity

def main():
    parser = argparse.ArgumentParser(description="Gmail Subscription Checker")
    sub = parser.add_subparsers(dest='cmd')

    parser.add_argument('-n','--max-results', type=int, default=20)

    sub.add_parser('list', help='List recent messages')
    sub.add_parser('parse', help='Show unsubscribe links')
    sub.add_parser('score', help='Score senders')
    sub.add_parser('unsubscribe', help='Bulk unsubscribe all found links')
    exp = sub.add_parser('export', help='Export subscription data')
    exp.add_argument('-f','--format', choices=['json','csv'], default='json')
    exp.add_argument('-o','--output', default='subscriptions.json')

    args = parser.parse_args()
    n = args.max_results

    if args.cmd == 'list':
        list_messages(n)
    elif args.cmd == 'parse':
        for i in parse_subscriptions_data(n):
            if i['unsubscribe_links']:
                print(i['id'], '|', i['subject'])
                for l in i['unsubscribe_links']:
                    print('  ↳', l)
    elif args.cmd == 'score':
        s = fetch_senders(n)
        if s: score_senders(s)
    elif args.cmd == 'unsubscribe':
        data = parse_subscriptions_data(n)
        links = [l for item in data for l in item['unsubscribe_links']]
        if not links:
            print("No unsubscribe links found.")
        else:
            confirm = input(f"Unsubscribe from {len(links)} links? [y/N]: ").lower()
            if confirm == 'y':
                results = bulk_unsubscribe(links)
                for link, res in results.items():
                    print(f"{link} → {res['status']}")
    elif args.cmd == 'export':
        data = parse_subscriptions_data(n)
        if args.format == 'json':
            with open(args.output,'w') as f: json.dump(data,f,indent=2)
        else:
            with open(args.output,'w',newline='') as f:
                w = csv.DictWriter(f, fieldnames=['id','subject','unsubscribe_links'])
                w.writeheader()
                for row in data: w.writerow(row)
        print(f"Exported to {args.output}")
    else:
        interactive_menu(n)

if __name__=='__main__':
    try: main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
