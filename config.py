import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "6331ea9062a3230572625b1361f739fd")

# Top 30 Leagues (API-Football IDs)
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
    128: "Liga Profesional",
    253: "MLS",
    179: "Scottish Premiership",
    40: "Championship",
    262: "Liga MX",
    98: "J1 League",
    113: "Super League Greece",
    207: "Swiss Super League",
    119: "Danish Superliga",
    103: "Eliteserien",
    106: "Ekstraklasa",
    136: "Serie B",
    141: "La Liga 2",
    79: "2. Bundesliga",
    62: "Ligue 2",
    94: "Primeira Liga",
    203: "Süper Lig",
    71: "Brasileirão Série A",
    128: "Argentine Liga",
    253: "Major League Soccer",
}
