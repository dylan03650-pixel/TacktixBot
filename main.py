import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import init_db, get_or_create_user, is_subscribed, activate_subscription, get_user, get_user_by_referral_code
from football_data import get_todays_fixtures
from ai_predictor import generate_analysis, get_trending_picks

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

MAIN_KEYBOARD = ReplyKeyboardMarkup([
    [KeyboardButton("💰 Deposit"), KeyboardButton("🔗 Referral")],
    [KeyboardButton("📊 Analyse"), KeyboardButton("🔥 Trending Offers")],
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
    text = f"⚽ Welcome {user.first_name}!\n\nAI Football Predictor is ready.\nUse the buttons below."
    await update.message.reply_text(text, reply_markup=MAIN_KEYBOARD)

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = get_user(user_id)

    if text == "💰 Deposit":
        status = "Active" if is_subscribed(user_id) else "Not subscribed"
        msg = f"💰 Deposit Menu\n\nPrice: $9.99/month\nStatus: {status}\n\nSend /subscribe to activate (demo)"
        await update.message.reply_text(msg)

    elif text == "🔗 Referral":
        code = user["referral_code"]
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start=ref_{code}"
        msg = f"🔗 Your Referral Link:\n{link}\n\nInvited: {user['referral_count']}\nInvite 30 people for 15% off"
        await update.message.reply_text(msg)

    elif text == "📊 Analyse":
        if not is_subscribed(user_id):
            await update.message.reply_text("🔒 Subscribe first. Send /subscribe")
            return
        await update.message.reply_text("Loading matches...")
        fixtures = await get_todays_fixtures()
        if not fixtures:
            await update.message.reply_text("No matches today.")
            return
        msg = "📊 Today's Matches:\n\n"
        for i, m in enumerate(fixtures[:8], 1):
            msg += f"{i}. {m['home']} vs {m['away']} ({m['league']})\n"
        msg += "\nReply with number to analyse"
        context.user_data["fixtures"] = fixtures
        await update.message.reply_text(msg)

    elif text == "🔥 Trending Offers":
        if not is_subscribed(user_id):
            await update.message.reply_text("🔒 Subscribe first. Send /subscribe")
            return
        fixtures = await get_todays_fixtures()
        picks = get_trending_picks(fixtures)
        msg = "🔥 Trending AI Picks:\n\n"
        for p in picks:
            msg += f"{p['match']}\nPick: {p['pick']} ({p['confidence']}%)\n\n"
        await update.message.reply_text(msg)

    elif text == "👤 My Account":
        status = "Active" if is_subscribed(user_id) else "Not subscribed"
        msg = f"👤 Account\nName: {user['first_name']}\nStatus: {status}\nReferrals: {user['referral_count']}"
        await update.message.reply_text(msg)

    elif text.isdigit() and "fixtures" in context.user_data:
        idx = int(text) - 1
        fixtures = context.user_data["fixtures"]
        if 0 <= idx < len(fixtures):
            analysis = generate_analysis(fixtures[idx])
            await update.message.reply_text(analysis, parse_mode="HTML")
        else:
            await update.message.reply_text("Invalid number")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activate_subscription(update.effective_user.id)
    await update.message.reply_text("✅ Subscription activated for 30 days (Demo)")

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
