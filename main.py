import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, TOP_LEAGUES
from database import init_db, get_or_create_user, is_subscribed, activate_subscription, get_user, get_user_by_referral_code
from football_data import get_leagues_list, get_fixtures_by_league
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


async def show_leagues(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    leagues = list(TOP_LEAGUES.items())
    per_page = 10
    start = page * per_page
    end = start + per_page
    current = leagues[start:end]

    keyboard = []
    row = []
    for i, (league_id, name) in enumerate(current):
        row.append(InlineKeyboardButton(name, callback_data=f"league_{league_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
    if end < len(leagues):
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)

    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"📊 Select a League\n\nPage {page+1}"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE, league_id: int):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("⏳ Loading matches...")

    fixtures = await get_fixtures_by_league(league_id, days=2)

    if not fixtures:
        await query.edit_message_text("No matches found in the next 2 days for this league.")
        return

    keyboard = []
    for match in fixtures[:12]:
        btn_text = f"{match['home']} vs {match['away']}"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"match_{match['id']}_{league_id}")])

    keyboard.append([InlineKeyboardButton("🔙 Back to Leagues", callback_data="back_leagues")])

    context.user_data["fixtures"] = {str(m["id"]): m for m in fixtures}

    league_name = TOP_LEAGUES.get(league_id, "League")
    await query.edit_message_text(
        f"🏆 {league_name}\nSelect a match:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE, fixture_id: str):
    query = update.callback_query
    await query.answer()

    fixtures = context.user_data.get("fixtures", {})
    match = fixtures.get(fixture_id)

    if not match:
        await query.edit_message_text("Match data not found. Please try again.")
        return

    analysis = generate_analysis(match)
    keyboard = [[InlineKeyboardButton("🔙 Back to Matches", callback_data=f"league_{match['league_id']}")]]

    await query.edit_message_text(analysis, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await show_leagues(update, context, page)

    elif data.startswith("league_"):
        league_id = int(data.split("_")[1])
        await show_matches(update, context, league_id)

    elif data.startswith("match_"):
        parts = data.split("_")
        fixture_id = parts[1]
        await show_analysis(update, context, fixture_id)

    elif data == "back_leagues":
        await show_leagues(update, context, 0)


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
            await update.message.reply_text("🔒 You need an active subscription.\nSend /subscribe to activate (demo).")
            return
        await show_leagues(update, context, 0)

    elif text == "🔥 Trending Offers":
        if not is_subscribed(user_id):
            await update.message.reply_text("🔒 Subscription required.\nSend /subscribe")
            return
        await update.message.reply_text("🔥 Generating best AI picks...")
        # For trending we can use a default league or improve later
        await update.message.reply_text("Trending feature will be improved next. Use Analyse for now.")

    elif text == "👤 My Account":
        status = "Active" if is_subscribed(user_id) else "Not subscribed"
        msg = f"👤 Account\nName: {user['first_name']}\nStatus: {status}\nReferrals: {user['referral_count']}"
        await update.message.reply_text(msg)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    activate_subscription(update.effective_user.id)
    await update.message.reply_text("✅ Subscription activated for 30 days (Demo)")


def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
