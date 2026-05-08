"""
╔══════════════════════════════════════════════════════════════╗
║              DARWIN BOT  —  YOUR BOT FILE                   ║
║                                                              ║
║   This is the ONLY file you need to edit.                   ║
║   Three things to change:  BODY, my_fitness(), GENERATIONS  ║
╚══════════════════════════════════════════════════════════════╝

HOW TO RUN
----------
    python bot.py

MODES
-----
Change MODE to:
    "test"     — 5 gens, checks everything works  (start here)
    "train"    — full training run, saves best.pkl
    "evaluate" — print stats on your saved best.pkl
    "watch"    — replay best.pkl in a window
"""

import sys, os, pickle, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
import arena

# ══════════════════════════════════════════════════════════════
#  STEP 1 — CHOOSE YOUR BODY
# ══════════════════════════════════════════════════════════════
#
#  n_legs     — how many legs (2 = biped, 4 = quadruped, 6 = hexapod)
#  thigh_len  — upper leg length in metres  (0.3 – 0.6)
#  shin_len   — lower leg length in metres  (0.2 – 0.5)
#  hip_range  — how far the thigh can swing (radians, 0.5 – 1.2)
#  knee_range — how far the knee can bend   (radians, 0.5 – 1.4)
#
#  The arena auto-calculates network inputs/outputs from n_legs.
#  More legs = more joints = bigger network = slower but more gaits.
#
#  Start with 4 legs. Once it walks, try 2 or 6.

BODY = {
    "n_legs":     4,
    "thigh_len":  0.45,
    "shin_len":   0.38,
    "hip_range":  0.85,
    "knee_range": 1.0,
}


# ══════════════════════════════════════════════════════════════
#  STEP 2 — WRITE YOUR FITNESS FUNCTION
# ══════════════════════════════════════════════════════════════
#
#  NEAT maximises whatever number you return. Higher = better.
#
#  You receive:
#    data["distance"]   — metres walked forward  (0.0 – ~10.0)
#    data["falls"]      — times the body collapsed  (0, 1, 2 ...)
#    data["smoothness"] — gait smoothness  (0.0 – 1.0)
#    data["step_count"] — clean forward steps taken  (0 – 600)
#
#  THE RULES:
#    1. A creature that falls should ALWAYS score less than one that walks.
#    2. Don't make all scores equal — NEAT needs a gradient to climb.
#    3. Experiment! Different formulas produce wildly different gaits.
#
#  THE CHALLENGE:
#    The starter function below is intentionally simple.
#    Can you write one that produces a faster or smoother walker?

CURRENT_GEN = [0]   # auto-updated each generation

def my_fitness(data):
    distance   = data["distance"]
    falls      = data["falls"]
    smoothness = data["smoothness"]
    step_count = data["step_count"]

    # Fallen creatures always lose to upright ones
    if falls > 0:
        return distance - falls * 2.0

    # Upright walkers: reward distance + consistent stepping
    score = distance * 10.0
    score += step_count * 0.05
    return score

    # ── IDEAS TO TRY ──────────────────────────────────────────
    # Reward smoothness:   score += smoothness * 5.0
    # Punish inefficiency: score -= (600 - step_count) * 0.01
    # Speed only:          return distance * 20.0
    # Efficiency:          return distance / max(step_count, 1) * 100
    # ──────────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════
#  STEP 3 — PICK MODE AND GENERATIONS
# ══════════════════════════════════════════════════════════════

MODE        = "train"
GENERATIONS = 100     # 50 = quick test, 200 = serious run


# ── Nothing below needs to change ─────────────────────────────

TEAM_FOLDER = os.path.dirname(os.path.abspath(__file__))
BEST_FILE   = os.path.join(TEAM_FOLDER, "best.pkl")

def _header(title):
    print("\n" + "=" * 56)
    print(f"  DARWIN BOT  —  {title}")
    print(f"  Legs: {BODY['n_legs']}   Mode: {MODE}")
    print("=" * 56)

def mode_train():
    _header(f"Training ({GENERATIONS} generations)")
    winner, config = arena.run_evolution(
        team_folder = TEAM_FOLDER,
        body_spec   = BODY,
        fitness_fn  = my_fitness,
        generations = GENERATIONS,
        verbose     = True,
        visual      = True,
        gen_counter = CURRENT_GEN,
    )
    with open(BEST_FILE, "wb") as f:
        pickle.dump((winner, config), f)
    print(f"  Saved best genome to best.pkl")
    print(f"  Switch MODE to 'watch' to see it walk.")

def mode_test():
    _header("Smoke test (5 generations)")
    arena.run_evolution(
        team_folder = TEAM_FOLDER,
        body_spec   = BODY,
        fitness_fn  = my_fitness,
        generations = 5,
        verbose     = True,
        visual      = False,
    )
    print("\n  Test passed! Switch MODE to 'train'.")

def mode_evaluate():
    _header("Evaluating best.pkl")
    if not os.path.exists(BEST_FILE):
        print("  No best.pkl found. Run 'train' first."); return
    with open(BEST_FILE, "rb") as f:
        winner, config = pickle.load(f)
    print("  Running 5 trials...\n")
    results = []
    for i in range(5):
        s = arena.evaluate_genome(winner, config, BODY, my_fitness)
        results.append(s)
        print(f"  Trial {i+1}: dist={s['distance']:.2f}m  "
              f"steps={s['step_count']}  falls={s['falls']}  "
              f"fit={s['fitness']:.3f}")
    avg_d = sum(r["distance"] for r in results) / 5
    print(f"\n  Average distance: {avg_d:.2f} m")
    score_path = os.path.join(TEAM_FOLDER, "score.json")
    if os.path.exists(score_path):
        with open(score_path, encoding="utf-8") as f:
            saved = json.load(f)
        print(f"  Best ever (training): {saved.get('distance','?')}m "
              f"over {saved.get('generation','?')} gens")

def mode_watch():
    _header("Watching best.pkl")
    if not os.path.exists(BEST_FILE):
        print("  No best.pkl found. Run 'train' first."); return
    with open(BEST_FILE, "rb") as f:
        winner, config = pickle.load(f)
    # Replay using arena internals
    from arena.engine import _replay_standalone
    _replay_standalone(winner, config, BODY)

if __name__ == "__main__":
    {"train": mode_train, "test": mode_test,
     "evaluate": mode_evaluate, "watch": mode_watch}.get(
        MODE, lambda: print(f"Unknown MODE '{MODE}'")
    )()
