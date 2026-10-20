#!/usr/bin/env bash
# AI Short Drama Dream Team — VPS one-click deploy
# Usage: bash setup.sh on a fresh VPS
set -euo pipefail

REPO_URL="https://github.com/dkooou/crewai-drama.git"
INSTALL_DIR="$HOME/nightshift-crew"

echo "=== 1/6 System update ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip git

echo "=== 2/6 Clone repo ==="
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR" && git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo "=== 3/6 Create venv & install ==="
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

echo "=== 4/6 Configure environment ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Edit .env and fill in your keys:"
    echo "    nano $INSTALL_DIR/.env"
    echo ""
    echo "Required:"
    echo "  - OPENROUTER_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo "  - ALLOWED_USER_IDS (your Telegram user ID)"
    echo "  - TAVILY_API_KEY (from tavily.com)"
    echo ""
fi

echo "=== 5/6 Install systemd services ==="
sudo cp deploy/nightshift-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nightshift-bot

echo "=== 6/6 Setup intelligence cron ==="
mkdir -p "$INSTALL_DIR/knowledge_base"/{daily,weekly,monthly,library}

CRON_CMD="cd $INSTALL_DIR && source .venv/bin/activate && nightshift-intel"
CRON_LINE="0 9 * * * $CRON_CMD >> $INSTALL_DIR/knowledge_base/cron.log 2>&1"

(crontab -l 2>/dev/null | grep -v "nightshift-intel" ; echo "$CRON_LINE") | crontab -

echo ""
echo "✅ Deploy complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env:        nano $INSTALL_DIR/.env"
echo "  2. Start bot:        sudo systemctl start nightshift-bot"
echo "  3. View logs:        journalctl -u nightshift-bot -f"
echo "  4. SSH direct run:   cd $INSTALL_DIR && source .venv/bin/activate && nightshift \"your task\""
echo "  5. Test intel:       cd $INSTALL_DIR && source .venv/bin/activate && nightshift-intel"
echo ""
echo "Intelligence cron: daily at 09:00 UTC"
echo "Knowledge base:    $INSTALL_DIR/knowledge_base/"
echo ""
