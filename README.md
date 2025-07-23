
A command-line tool to find, score, and manage subscription emails in your Gmail account.

## 🚀 Features
- **OAuth2 Authentication** with the Gmail API  
- **Fetch & List** your recent messages  
- **Detect Subscriptions** via `List-Unsubscribe` headers and keywords  
- **Extract Unsubscribe Links** automatically  
- **Score & Flag** high-volume senders  
- **Bulk Actions**: unsubscribe, archive, label  
- **Basic Analytics**: track email volume over time  

## 🛠 Prerequisites
- **Python 3.8+**  
- **Git**  
- A **Google account** with Gmail API enabled  

## 🔧 Installation
```bash
git clone https://github.com/<your-username>/gmail-subscription-checker.git
cd gmail-subscription-checker
python3 -m venv venv
source venv/bin/activate        # Windows PowerShell: .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
