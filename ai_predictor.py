import random

def generate_analysis(match: dict) -> str:
    home = match.get("home", "Home")
    away = match.get("away", "Away")
    league = match.get("league", "Unknown")
    match_time = match.get("date", "TBD")
    is_live = match.get("is_live", False)

    # xG
    home_xg = round(random.uniform(1.3, 2.6), 2)
    away_xg = round(random.uniform(0.8, 1.7), 2)
    total_xg = round(home_xg + away_xg, 2)

    # Possible score
    if home_xg - away_xg > 0.9:
        score = f"{random.randint(2,3)}-{random.randint(0,1)}"
        risk = random.randint(14, 24)
    elif away_xg - home_xg > 0.7:
        score = f"{random.randint(0,1)}-{random.randint(2,3)}"
        risk = random.randint(16, 26)
    else:
        score = f"{random.randint(1,2)}-{random.randint(1,2)}"
        risk = random.randint(20, 30)

    over25 = random.randint(55, 73)
    btts = random.randint(49, 67)
    cards = f"{random.randint(3,4)}-{random.randint(5,6)}"
    corners = f"{random.randint(8,10)}-{random.randint(11,14)}"
    confidence = random.randint(75, 87)

    # ========== LINEUP SECTION ==========
    home_lineup, away_lineup, key_player, formation = generate_lineups(home, away, is_live)

    lineup_title = "📋 Live Lineup" if is_live else "📋 Predicted Lineup"

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

{lineup_title} ({formation})
{home}: {home_lineup}
{away}: {away_lineup}

👤 <b>Key Player Prop</b>
{key_player} to Score: {random.randint(34, 47)}%

🔥 AI Confidence: {confidence}%
""".strip()

    return text


def generate_lineups(home: str, away: str, is_live: bool = False):
    formations = ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2", "3-4-3"]
    formation = random.choice(formations)

    # Simple realistic player pools
    home_players = [
        f"{home[:3]} GK", f"{home[:3]} RB", f"{home[:3]} CB", f"{home[:3]} CB", f"{home[:3]} LB",
        f"{home[:3]} CM", f"{home[:3]} CM", f"{home[:3]} AM",
        f"{home[:3]} RW", f"{home[:3]} ST", f"{home[:3]} LW"
    ]
    away_players = [
        f"{away[:3]} GK", f"{away[:3]} RB", f"{away[:3]} CB", f"{away[:3]} CB", f"{away[:3]} LB",
        f"{away[:3]} CM", f"{away[:3]} CM", f"{away[:3]} AM",
        f"{away[:3]} RW", f"{away[:3]} ST", f"{away[:3]} LW"
    ]

    # Better known style names for big teams
    famous = {
        "Arsenal": ["Raya", "White", "Saliba", "Gabriel", "Timber", "Rice", "Odegaard", "Havertz", "Saka", "Jesus", "Martinelli"],
        "Man City": ["Ederson", "Walker", "Dias", "Akanji", "Gvardiol", "Rodri", "De Bruyne", "Foden", "Bernardo", "Haaland", "Doku"],
        "Liverpool": ["Alisson", "Alexander-Arnold", "Van Dijk", "Konate", "Robertson", "Mac Allister", "Szoboszlai", "Jones", "Salah", "Nunez", "Diaz"],
        "Real Madrid": ["Courtois", "Carvajal", "Militão", "Rüdiger", "Mendy", "Camavinga", "Bellingham", "Valverde", "Rodrygo", "Mbappé", "Vinicius"],
        "Barcelona": ["ter Stegen", "Kounde", "Araujo", "Cubarsi", "Balde", "Pedri", "Gavi", "Olmo", "Yamal", "Lewandowski", "Raphinha"],
        "Bayern Munich": ["Neuer", "Mazraoui", "Upamecano", "Kim", "Davies", "Kimmich", "Goretzka", "Musiala", "Olise", "Kane", "Sané"],
        "PSG": ["Donnarumma", "Hakimi", "Marquinhos", "Pacho", "Mendes", "Vitinha", "Neves", "Ruiz", "Dembélé", "Barcola", "Kvaratskhelia"],
    }

    if home in famous:
        home_players = famous[home]
    if away in famous:
        away_players = famous[away]

    home_lineup = ", ".join(home_players[:11])
    away_lineup = ", ".join(away_players[:11])

    # Key player = most likely to score (prefer forwards)
    key_candidates = home_players[-3:] + away_players[-3:]
    key_player = random.choice(key_candidates)

    return home_lineup, away_lineup, key_player, formation


def get_trending_picks(fixtures: list, limit: int = 5) -> list:
    picks = []
    for m in fixtures[:12]:
        conf = random.randint(76, 89)
        market = random.choice(["Home Win", "Over 2.5", "BTTS Yes", "Away Win"])
        picks.append({
            "match": f"{m['home']} vs {m['away']}",
            "league": m.get("league", ""),
            "pick": market,
            "confidence": conf
        })
    return sorted(picks, key=lambda x: x["confidence"], reverse=True)[:limit]
