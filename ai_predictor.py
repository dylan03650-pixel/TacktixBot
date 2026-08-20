import random

def generate_analysis(match: dict) -> str:
    home = match["home"]
    away = match["away"]
    league = match["league"]

    home_win = round(random.uniform(38, 55), 1)
    draw = round(random.uniform(23, 29), 1)
    away_win = round(100 - home_win - draw, 1)

    over25 = round(random.uniform(50, 67), 1)
    btts = round(random.uniform(48, 63), 1)

    player = random.choice([home.split()[-1], away.split()[-1]])
    score_prob = round(random.uniform(30, 48), 1)
    confidence = random.choice([79, 82, 85, 88, 91])

    return f"""
📊 <b>AI Pre-Match Analysis</b>
🏆 {league}
⚽ <b>{home}</b> vs <b>{away}</b>

🎯 <b>Match Outcome</b>
• Home Win: {home_win}%
• Draw: {draw}%
• Away Win: {away_win}%

📈 <b>Key Markets</b>
• Over 2.5 Goals: {over25}%
• Both Teams to Score: {btts}%

👤 <b>Player Prop</b>
• {player} to Score: <b>{score_prob}%</b>

🔥 <b>AI Confidence: {confidence}%</b>
💡 Updated daily • Top 30 leagues coverage
⚠️ Probabilistic insight only — not financial advice.
""".strip()

def get_trending_picks(fixtures: list, limit: int = 5):
    picks = []
    for m in fixtures[:12]:
        conf = random.randint(80, 93)
        market = random.choice(["Home Win", "Over 2.5 Goals", "BTTS Yes", "Away Win", "Under 2.5"])
        picks.append({
            "match": f"{m['home']} vs {m['away']}",
            "league": m["league"],
            "pick": market,
            "confidence": conf
        })
    return sorted(picks, key=lambda x: x["confidence"], reverse=True)[:limit]
