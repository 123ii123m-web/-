#!/data/data/com.termux/files/usr/bin/bash

REPO="https://github.com/$GITHUB_REPO"
BRANCH="main"
BOT_DIR="$HOME/bot"

echo "🤖 Updating bot from $REPO..."

cd "$BOT_DIR" || {
    echo "📁 Cloning for first time..."
    git clone -b "$BRANCH" "$REPO" "$BOT_DIR"
    cd "$BOT_DIR" || exit 1
}

echo "📥 Pulling latest changes..."
git pull origin "$BRANCH"

echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

echo "🔄 Restarting bot..."
pkill -f "python.*main.py" 2>/dev/null
sleep 1
nohup python main.py > bot.log 2>&1 &

echo "✅ Done! Bot PID: $!"
