import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import init_db, get_or_create_user, is_subscribed, activate_subscription, get_user, get_user_by_referral_code
from football_data import get_todays_fixtures
from ai_predictor import generate_analysis, get_trending_picks

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("💰 Deposit"), KeyboardButton("🔗 Referral")],
        [KeyboardButton("📊 Analyse"), KeyboardButton("🔥 Trending Offers")],
        [KeyboardButton("👤 My Account")],
    ],
    resize_keyboard=True
)


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
        f"⚽ Welcome to <b>AI Football Predictor</b>, {user.first_name}!\n\n"
        "Daily AI analysis on the top 30 football leagues.\n"
        "Subscribe monthly to unlock full analysis & trending picks."
    )
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD, parse_mode="HTML")


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)

    if text == "💰 Deposit":
        status = "✅ Active" if is_subscribed(user_id) else "❌ Not subscribed"
        msg = (
            f"<b>💰 Deposit / Subscription</b>\n\n"
            f"Monthly Price: <b>$9.99</b>\n"
            f"Your status: {status}\n\n"
            "To activate (demo mode):\n"
            "Send /subscribe\n\n"
            "In real version you will pay with card/crypto here."
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "🔗 Referral":
        code = user["referral_code"]
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=ref_{code}"
        count = user["referral_count"]
        msg = (
            f"<b>🔗 Your Referral Program</b>\n\n"
            f"Your unique link:\n<code>{link}</code>\n\n"
            f"People invited: <b>{count}</b>\n"
            f"Invite <b>30</b> friends → Get <b>15% off</b> forever\n\n"
            "Share the link with friends!"
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "📊 Analyse":
        if not is_subscribed(user_id):
            await update.message.reply_text("🔒 You need an active subscription.\nGo to 💰 Deposit menu.")
            return

        await update.message.reply_text("⏳ Loading today's matches...")
        fixtures = await get_todays_fixtures()

        if not fixtures:
            await update.message.reply_text("No matches found for today.")
            return

        msg = "<b>📊 Today's Matches (Top Leagues)</b>\n\n"
        for i, m in enumerate(fixtures[:10], 1):
            msg += f"{i}. {m['home']} vs {m['away']}\n   🏆 {m['league']} • ⏰ {m['time']}\n\n"

        msg += "Reply with the number (e.g. 1) to get full AI analysis."
        context.user_data["fixtures"] = fixtures
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "🔥 Trending Offers":
        if not is_subscribed(user_id):
            await update.message.reply_text("🔒 Subscription required.\nGo to 💰 Deposit.")
            return

        await update.message.reply_text("🔥 Generating best AI picks...")
        fixtures = await get_todays_fixtures()
        picks = get_trending_picks(fixtures)

        msg = "<b>🔥 AI Trending Offers (Highest Confidence)</b>\n\n"
        for p in picks:
            msg += (
                f"⚽ <b>{p['match']}</b>\n"
                f"🏆 {p['league']}\n"
                f"🎯 Pick: <b>{p['pick']}</b>\n"
                f"🔥 Confidence: <b>{p['confidence']}%</b>\n\n"
            )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text == "👤 My Account":
        status = "✅ Active until " + user["subscription_expires"][:10] if is_subscribed(user_id) else "❌ Not subscribed"
        msg = (
            f"<b>👤 My Account</b>\n\n"
            f"Name: {user['first_name']}\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Subscription: {status}\n"
            f"Referrals: {user['referral_count']}\n"
            f"Referral Code: <code>{user['referral_code']}</code>"
        )
        await update.message.reply_text(msg, parse_mode="HTML")

    elif text.isdigit() and "fixtures" in context.user_data:
        idx = int(text) - 1
        fixtures = context.user_data["fixtures"]
        if 0 <= idx < len(fixtures):
            analysis = generate_analysis(fixtures[idx])
            await update.message.reply_text(analysis, parse_mode="HTML")
        else:
            await update.message.reply_text("Invalid number. Please try again.")


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    activate_subscription(user_id)
    await update.message.reply_text("✅ Subscription activated for 30 days! (Demo mode)")


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_menu))

    print("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
