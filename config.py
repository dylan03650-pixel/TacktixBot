import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

MONTHLY_PRICE = 9.99
CURRENCY = "USD"
REFERRAL_DISCOUNT_THRESHOLD = 30
REFERRAL_DISCOUNT_PERCENT = 15

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")

TOP_LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    88: "Eredivisie",
    94: "Primeira Liga",
    144: "Belgian Pro League",
    203: "Süper Lig",
    71: "Brasileirão",
    128: "Liga Profesional Argentina",
    253: "MLS",
    2: "Champions League",
    3: "Europa League",
}
