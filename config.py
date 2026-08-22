import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BIGBALLS_API_KEY = os.getenv("BIGBALLS_API_KEY", "bbs_live_00000jXel6VRtTq2bcDzHMOEIiY1iO0ah9uPoThP5xZFzlRA")

# Only leagues that work well on Big Balls free plan
TOP_LEAGUES = {
    "epl": "Premier League",
    "laliga": "La Liga",
    "seriea": "Serie A",
    "bundesliga": "Bundesliga",
    "ligue1": "Ligue 1",
    "ucl": "Champions League",
    "mls": "MLS",
}
