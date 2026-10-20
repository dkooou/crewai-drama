#!/usr/bin/env bash
# 《夜班守则》CrewAI — Vultr VPS 一键部署
# 用法：在新 VPS 上执行 bash setup.sh
set -euo pipefail

echo "=== 1/5 系统更新 ==="
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12 python3.12-venv python3-pip git

echo "=== 2/5 克隆代码 ==="
cd ~
if [ -d "nightshift-crew" ]; then
    cd nightshift-crew && git pull
else
    git clone https://github.com/你的用户名/nightshift-crew.git
    cd nightshift-crew
fi

echo "=== 3/5 创建虚拟环境 & 安装依赖 ==="
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .

echo "=== 4/5 配置环境变量 ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  请编辑 .env 填入你的 key："
    echo "    nano ~/nightshift-crew/.env"
    echo ""
    echo "需要填写："
    echo "  - OPENROUTER_API_KEY"
    echo "  - TELEGRAM_BOT_TOKEN（从 @BotFather 获取）"
    echo "  - ALLOWED_USER_IDS（你的 Telegram 用户 ID）"
    echo ""
fi

echo "=== 5/5 安装 systemd 服务 ==="
sudo cp deploy/nightshift-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nightshift-bot

echo ""
echo "✅ 部署完成！"
echo ""
echo "接下来："
echo "  1. 编辑 .env：    nano ~/nightshift-crew/.env"
echo "  2. 启动 bot：     sudo systemctl start nightshift-bot"
echo "  3. 查看日志：     journalctl -u nightshift-bot -f"
echo "  4. SSH 直接跑：   cd ~/nightshift-crew && source .venv/bin/activate && nightshift"
echo ""
