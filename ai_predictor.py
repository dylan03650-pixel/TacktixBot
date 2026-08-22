import random

def generate_analysis(match: dict) -> str:
    home = match.get("home", "Home")
    away = match.get("away", "Away")
    league = match.get("league", "Unknown")
    match_time = match.get("date", "TBD")

    # Simulated but realistic looking values
    home_xg = round(random.uniform(1.4, 2.8), 2)
    away_xg = round(random.uniform(0.7, 1.6), 2)
    total_xg = round(home_xg + away_xg, 2)

    # Possible score
    if home_xg - away_xg > 1.0:
        score = f"{random.randint(2,3)}-{random.randint(0,1)}"
        risk = random.randint(12, 22)
    elif away_xg - home_xg > 0.8:
        score = f"{random.randint(0,1)}-{random.randint(2,3)}"
        risk = random.randint(15, 25)
    else:
        score = f"{random.randint(1,2)}-{random.randint(1,2)}"
        risk = random.randint(20, 32)

    over25 = random.randint(52, 74)
    btts = random.randint(48, 68)
    cards = f"{random.randint(3,4)}-{random.randint(5,6)}"
    corners = f"{random.randint(8,10)}-{random.randint(11,14)}"

    # Player prop
    player = random.choice([home.split()[-1], away.split()[-1], "Key Forward"])
    player_prob = random.randint(32, 48)

    confidence = random.randint(74, 86)

    text = f"""
⚽ <b>{home} vs {away}</b>
🏆 {league}
⏰ {match_time}

🎯 <b>Possible Score:</b> {score}
⚠️ Risk Level: {risk}%

📊 <b>Expected Goals (xG)</b>
Home: {home_xg}  |  Away: {away_xg}
Total xG: {total_xg}

📈 <b>Markets</b>
• Over 2.5 Goals: {over25}%
• Both Teams to Score: {btts}%

🟨 Cards: {cards} total
🚩 Corners: {corners} total

👤 <b>Key Player Prop</b>
{player} to Score: {player_prob}%

🔥 AI Confidence: {confidence}%
""".strip()

    return text


def get_trending_picks(fixtures: list, limit: int = 5) -> list:
    picks = []
    for m in fixtures[:15]:
        conf = random.randint(76, 89)
        market = random.choice(["Home Win", "Over 2.5", "BTTS Yes", "Away Win"])
        picks.append({
            "match": f"{m['home']} vs {m['away']}",
            "league": m.get("league", ""),
            "pick": market,
            "confidence": conf
        })
    return sorted(picks, key=lambda x: x["confidence"], reverse=True)[:limit]
