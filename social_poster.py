"""
Social Media Auto-Poster Bot
Automatically posts to Facebook, Twitter/X, and Telegram
Usage: python social_poster.py

Install requirements:
pip install tweepy facebook-sdk python-telegram-bot schedule
"""

import schedule
import time
import tweepy
import telegram
import asyncio
from datetime import datetime

# ============================================================
# ⚙️ CONFIGURATION - Fill in your API keys here
# ============================================================

TWITTER_CONFIG = {
    "api_key": "YOUR_TWITTER_API_KEY",
    "api_secret": "YOUR_TWITTER_API_SECRET",
    "access_token": "YOUR_ACCESS_TOKEN",
    "access_secret": "YOUR_ACCESS_TOKEN_SECRET"
}

TELEGRAM_CONFIG = {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "channel_id": "@your_channel_name"  # or use numeric ID like -1001234567890
}

# ============================================================
# 📝 YOUR POSTS SCHEDULE
# Edit these posts - they will be posted automatically!
# ============================================================

POSTS = [
    {
        "text": "🚀 Good morning! Check out our latest deals today! #business #deals",
        "post_at": "09:00",  # Posts at 9 AM every day
        "platforms": ["twitter", "telegram"]
    },
    {
        "text": "💡 Did you know? Automation saves businesses 10+ hours per week! Contact us for a free demo.",
        "post_at": "13:00",  # Posts at 1 PM
        "platforms": ["twitter", "telegram"]
    },
    {
        "text": "🌙 Good night! Stay tuned for tomorrow's updates. Follow us for more!",
        "post_at": "21:00",  # Posts at 9 PM
        "platforms": ["telegram"]
    }
]

# ============================================================
# 🐦 TWITTER / X POSTER
# ============================================================

def post_to_twitter(text):
    """Post a tweet to Twitter/X"""
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_CONFIG["api_key"],
            consumer_secret=TWITTER_CONFIG["api_secret"],
            access_token=TWITTER_CONFIG["access_token"],
            access_token_secret=TWITTER_CONFIG["access_secret"]
        )
        response = client.create_tweet(text=text[:280])  # Twitter limit
        print(f"✅ Twitter: Posted successfully! ID: {response.data['id']}")
        return True
    except Exception as e:
        print(f"❌ Twitter Error: {e}")
        return False

# ============================================================
# 📱 TELEGRAM POSTER
# ============================================================

async def post_to_telegram_async(text):
    """Post a message to Telegram channel"""
    try:
        bot = telegram.Bot(token=TELEGRAM_CONFIG["bot_token"])
        await bot.send_message(
            chat_id=TELEGRAM_CONFIG["channel_id"],
            text=text,
            parse_mode='HTML'
        )
        print(f"✅ Telegram: Posted successfully!")
        return True
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        return False

def post_to_telegram(text):
    asyncio.run(post_to_telegram_async(text))

# ============================================================
# 📅 SCHEDULER
# ============================================================

def make_post_job(post):
    """Create a job function for a post"""
    def job():
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"\n📤 Posting at {now}...")
        print(f"   Text: {post['text'][:50]}...")
        
        for platform in post['platforms']:
            if platform == "twitter":
                post_to_twitter(post['text'])
            elif platform == "telegram":
                post_to_telegram(post['text'])
        
    return job

def manual_post():
    """Post something right now manually"""
    print("\n✍️  MANUAL POST")
    text = input("Enter your post text: ")
    platforms = input("Platforms (twitter/telegram/both): ").lower()
    
    if "twitter" in platforms or "both" in platforms:
        post_to_twitter(text)
    if "telegram" in platforms or "both" in platforms:
        post_to_telegram(text)

def setup_schedule():
    """Set up the automatic posting schedule"""
    for post in POSTS:
        job = make_post_job(post)
        schedule.every().day.at(post['post_at']).do(job)
        print(f"⏰ Scheduled: '{post['text'][:40]}...' at {post['post_at']}")

# ============================================================
# 🚀 MAIN
# ============================================================

def main():
    print("=" * 50)
    print("📱 SOCIAL MEDIA AUTO-POSTER BOT")
    print("=" * 50)
    print("\nWhat do you want to do?")
    print("1. Start auto-scheduler (posts automatically)")
    print("2. Post something manually right now")
    print("3. Test connection")
    
    choice = input("\nChoose (1/2/3): ")
    
    if choice == "1":
        print("\n🤖 Starting auto-scheduler...")
        setup_schedule()
        print("\n✅ Bot is running! Press Ctrl+C to stop.")
        print("Posts will be sent at scheduled times.\n")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    elif choice == "2":
        manual_post()
    
    elif choice == "3":
        print("\n🔍 Testing connections...")
        test_text = f"Test post from AutoPoster Bot - {datetime.now()}"
        post_to_twitter(test_text)
        post_to_telegram(test_text)
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
