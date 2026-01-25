import json

# ---- CONFIG ----
INPUT_JSON_PATH = "f1_2026_calendar.json"
OUTPUT_JSON_PATH = "f1_2026_calendar_with_tracks.json"

def load_base64(path):
    with open(path, "r") as f:
        return f.read().strip()

TRACK_MAP = {
    "Albert Park Circuit": load_base64("tracks/australia.txt"),
    "Shanghai International Circuit": load_base64("tracks/china.txt"),
    "Suzuka Circuit": load_base64("tracks/japan.txt"),
    "Bahrain International Circuit": load_base64("tracks/bahrain.txt"),
    "Jeddah Corniche Circuit": load_base64("tracks/jeddah.txt"),
    "Miami International Autodrome": load_base64("tracks/miami.txt"),
    "Circuit Gilles Villeneuve": load_base64("tracks/canada.txt"),
    "Circuit de Monaco": load_base64("tracks/monaco.txt"),
    "Circuit de Barcelona-Catalunya": load_base64("tracks/barcalona.txt"),
    "Red Bull Ring": load_base64("tracks/redbullring.txt"),
    "Silverstone Circuit": load_base64("tracks/silverstone.txt"),
    "Circuit de Spa-Francorchamps": load_base64("tracks/spa.txt"),
    "Hungaroring": load_base64("tracks/hungary.txt"),
    "Circuit Zandvoort": load_base64("tracks/zandvoort.txt"),
    "Autodromo Nazionale Monza": load_base64("tracks/monza.txt"),
    "Madrid Street Circuit": load_base64("tracks/madrid.txt"),
    "Baku City Circuit": load_base64("tracks/baku.txt"),
    "Marina Bay Street Circuit": load_base64("tracks/singapore.txt"),
    "Circuit of the Americas": load_base64("tracks/cota.txt"),
    "Autódromo Hermanos Rodríguez": load_base64("tracks/mexico.txt"),
    "Autódromo José Carlos Pace": load_base64("tracks/brazil.txt"),
    "Las Vegas Street Circuit": load_base64("tracks/vegas.txt"),
    "Lusail International Circuit": load_base64("tracks/qatar.txt"),
    "Yas Marina Circuit": load_base64("tracks/abu.txt")
}

# ---- LOAD DATA ----
with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
    calendar = json.load(f)

# ---- UPDATE TRACKS ----
for session in calendar:
    circuit = session.get("circuit")

    if circuit in TRACK_MAP:
        session["track"] = TRACK_MAP[circuit]

# ---- SAVE OUTPUT ----
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(calendar, f, indent=2, ensure_ascii=False)

print(f"Updated calendar written to {OUTPUT_JSON_PATH}")
