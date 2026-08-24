import logging
import aiohttp
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import (
    init_db, get_or_create_user, is_subscribed, activate_subscription,
    get_user, get_user_by_referral_code, set_news_enabled, is_news_enabled
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("💰 Deposit"), KeyboardButton("🔗 Referral")],
    [KeyboardButton("🙌 Testimonials"), KeyboardButton("📰 Current News")],
    [KeyboardButton("👤 My Account")]
], resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_by = None
    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            code = arg[4:]
            ref_user = get_user_by_referral_code(code)
            if ref_user and ref_user["user_id"] != user.id:
                referred_by = ref_user["user_id"]
    get_or_create_user(user.id, user.username, user.first_name, referred_by)

    text = (
        f"⚽ <b>Welcome to TacktixBot</b>, {user.first_name}!\n\n"
        "Your smart football companion for news, insights & exclusive offers.\n\n"
        "Use the menu below to explore 👇"
    )
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD, parse_mode="HTML")


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)

    if text == "💰 Deposit":
        msg = (
            "💰 <b>Deposit & Subscribe</b>\n\n"
            "📦 <b>Monthly Plan:</b> ₦15,000\n\n"
            "Unlock full access and premium features.\n\n"
            "👉 <b>Official Payment Link:</b>\n"
            "https://re-direct.base44.app/\n\n"
            "After successful payment, your account will be upgraded automatically."
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "🔗 Referral":
        code = user["referral_code"]
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=ref_{code}"
        count = user["referral_count"]
        msg = (
            "🔗 <b>Referral Program</b>\n\n"
            f"👥 People invited: <b>{count}</b>\n"
            f"🎁 Invite <b>30 friends</b> → Get <b>30% OFF</b> forever\n\n"
            "Your unique referral link:\n"
            f"<code>{link}</code>\n\n"
            "Share it with friends and earn rewards! 🚀"
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "🙌 Testimonials":
        msg = (
            "🙌 <b>Testimonials</b>\n\n"
            "Real stories from TacktixBot users will appear here soon.\n\n"
            "Stay tuned for authentic feedback and success stories 🔥"
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "📰 Current News":
        enabled = is_news_enabled(user_id)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔔 Enable Auto News", callback_data="news_on"),
                InlineKeyboardButton("🔕 Disable Auto News", callback_data="news_off")
            ],
            [InlineKeyboardButton("📄 View Latest News", callback_data="show_news")]
        ])
        msg = (
            "📰 <b>Current News</b>\n\n"
            f"Auto News: {status}\n\n"
            "• Enable → Receive top football news every 2-3 hours\n"
            "• Disable → Stop automatic updates\n"
            "• View Latest → Get today’s top stories now"
        )
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode="HTML")

    elif text == "👤 My Account":
        plan = "✅ Subscribed" if is_subscribed(user_id) else "🆓 Free Plan"
        joined = user.get("created_at", "Unknown")[:10] if user.get("created_at") else "Unknown"
        msg = (
            "👤 <b>My Account</b>\n\n"
            f"👤 Name: <b>{user['first_name']}</b>\n"
            f"🆔 User ID: <code>{user_id}</code>\n"
            f"📅 Date Joined: <b>{joined}</b>\n"
            f"💎 Current Plan: <b>{plan}</b>\n"
            f"👥 Referrals: <b>{user['referral_count']}</b>\n"
            f"🔗 Referral Code: <code>{user['referral_code']}</code>"
        )
        await update.message.reply_text(msg, parse_mode="HTML")


async def fetch_real_news():
    feeds = [
        "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "http://feeds.bbci.co.uk/sport/0/football/rss.xml",
    ]
    news = []
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession() as session:
        for url in feeds:
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        items = re.findall(
                            r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?(?:<description>(.*?)</description>)?.*?</item>",
                            text, re.DOTALL
                        )
                        for title, link, desc in items[:6]:
                            title = re.sub(r"<!\[CDATA\[|\]\]>", "", title).strip()
                            link = re.sub(r"<!\[CDATA\[|\]\]>", "", link).strip()
                            summary = re.sub(r"<!\[CDATA\[|\]\]>|<.*?>", "", desc or "").strip()[:120]
                            if title and link:
                                news.append({
                                    "title": title,
                                    "link": link,
                                    "summary": summary + "..." if summary else "Click to read full story."
                                })
                        if news:
                            break
            except Exception as e:
                print(f"News fetch error: {e}")
                continue
    return news


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "news_on":
        set_news_enabled(user_id, True)
        await query.edit_message_text(
            "✅ Auto News has been turned <b>ON</b>.\nYou will receive top football news every 2-3 hours.",
            parse_mode="HTML"
        )

    elif data == "news_off":
        set_news_enabled(user_id, False)
        await query.edit_message_text(
            "🔕 Auto News has been turned <b>OFF</b>.",
            parse_mode="HTML"
        )

    elif data == "show_news":
        await query.edit_message_text("⏳ Fetching latest football news...")
        news_items = await fetch_real_news()

        if not news_items:
            msg = "📰 <b>Today’s Top Football News</b>\n\nUnable to fetch live news right now.\nPlease try again later."
        else:
            msg = "📰 <b>Today’s Top Football News</b>\n\n"
            for item in news_items[:5]:
                msg += (
                    f"🔹 <b>{item['title']}</b>\n"
                    f"{item['summary']}\n"
                    f"<a href='{item['link']}'>Read more →</a>\n\n"
                )
            msg += "_News powered by BBC Sport & top sources_"

        await query.edit_message_text(msg, parse_mode="HTML", disable_web_page_preview=False)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activate_subscription(update.effective_user.id)
    await update.message.reply_text("✅ Subscription activated for 30 days! (Demo)")


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("TacktixBot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
