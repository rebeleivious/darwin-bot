import json, os, time

def show():
    scores = []
    for team in os.listdir("teams"):
        p = os.path.join("teams", team, "score.json")
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                d["team"] = team
                scores.append(d)
            except: pass
    scores.sort(key=lambda x: x.get("distance", 0), reverse=True)
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 52)
    print("       DARWIN BOT  —  LEADERBOARD")
    print("=" * 52)
    medals = ["1st", "2nd", "3rd"]
    for i, s in enumerate(scores):
        m = medals[i] if i < 3 else f" {i+1}."
        print(f"  {m}  {s['team']:<18}  {s.get('distance',0):.2f}m  gen {s.get('generation',0)}")
    print("=" * 52)

if __name__ == "__main__":
    while True:
        show()
        time.sleep(5)
