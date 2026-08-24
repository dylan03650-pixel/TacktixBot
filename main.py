import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import (
    init_db, get_or_create_user, is_subscribed, activate_subscription,
    get_user, get_user_by_referral_code, set_news_enabled, is_news_enabled
)
from football_data import get_fixtures_by_league
from ai_predictor import generate_analysis, get_trending_picks
from datetime import datetime

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
            "💰 <b>Deposit</b>\n\n"
            "Monthly Plan: <b>₦15,000</b>\n\n"
            "Click the link below to deposit on our official site:\n\n"
            "👉 https://re-direct.base44.app/\n\n"
            "After successful payment, your account will be upgraded."
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
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode="HTML")

    elif text == "👤 My Account":
        plan = "✅ Subscribed" if is_subscribed(user_id) else "🆓 Free Plan"
        joined = user.get("created_at", "Unknown")[:10] if user.get("created_at") else "Unknown"

        msg = (
            f"👤 <b>My Account</b>\n\n"
            f"Name: {user['first_name']}\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Date Joined: {joined}\n"
            f"Current Plan: {plan}\n"
            f"Referrals: {user['referral_count']}\n"
            f"Referral Code: <code>{user['referral_code']}</code>"
        )
        await update.message.reply_text(msg, parse_mode="HTML")


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
        news_items = [
            {
                "topic": "🚨 Injury News",
                "title": "Star forward ruled out for 3 weeks",
                "summary": "A major Premier League club has confirmed their key attacker will miss the next three matches.",
                "link": "https://www.bbc.com/sport/football"
            },
            {
                "topic": "🔄 Transfer Update",
                "title": "Big-money move close to completion",
                "summary": "A top European club is finalising a deal for a highly-rated midfielder.",
                "link": "https://www.skysports.com/football"
            },
            {
                "topic": "🏆 Match Preview",
                "title": "Title race heats up this weekend",
                "summary": "Two title contenders face crucial tests in the coming days.",
                "link": "https://www.goal.com/en"
            },
            {
                "topic": "📰 League News",
                "title": "Manager under pressure after poor run",
                "summary": "Recent results have put a high-profile coach’s future in doubt.",
                "link": "https://www.espn.com/soccer/"
            },
        ]

        msg = "📰 <b>Today’s Top Football News</b>\n\n"
        for item in news_items:
            msg += (
                f"{item['topic']}\n"
                f"<b>{item['title']}</b>\n"
                f"{item['summary']}\n"
                f"<a href='{item['link']}'>Read more →</a>\n\n"
            )

        msg += "_News updates regularly. Stay tuned!_"

        await query.edit_message_text(
            msg,
            parse_mode="HTML",
            disable_web_page_preview=False
    )

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
