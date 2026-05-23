"""
╔══════════════════════════════════════════════════════════════════════╗
║                    DARWIN BOT  —  YOUR BOT FILE                     ║
║                                                                      ║
║  This is the ONLY file you need to edit.                            ║
║  Everything else (physics, NEAT, rendering) is handled for you.     ║
╚══════════════════════════════════════════════════════════════════════╝

HOW TO RUN
----------
    python bot.py

FIRST TIME? Do this in order:
    1. Set MODE = "test"     — checks everything works (5 gens, ~30s)
    2. Set MODE = "train"    — real training run, saves best.pkl
    3. Set MODE = "watch"    — watch your best creature walk
    4. Set MODE = "evaluate" — print final distance stats

THE BIG PICTURE
---------------
You are teaching a creature to walk using EVOLUTION.

Every generation, the engine runs hundreds of creatures. Each one
has a neural network brain that controls its legs. The networks that
score highest according to YOUR fitness function survive and reproduce.
Their offspring are slightly mutated copies. Over many generations,
the population gets better and better at whatever you reward.

You don't program the walk — you define what "good" means, and
evolution figures out how to achieve it. Your job is to write a
fitness function that makes "good" mean "walks far".

YOUR THREE JOBS
---------------
  STEP 1 — Design the body   (BODY dict below)
  STEP 2 — Define fitness    (my_fitness function below)
  STEP 3 — Pick generations  (GENERATIONS constant below)
"""

import sys, os, pickle, json
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
import arena


# ══════════════════════════════════════════════════════════════════════
#  STEP 1 — DESIGN YOUR BODY
# ══════════════════════════════════════════════════════════════════════
#
#  This controls the physical shape of your creature.
#  Think of it like choosing the body before the brain evolves.
#
#  n_legs     — number of legs
#                 2 = biped      (like a human — hard to balance, fast once it works)
#                 4 = quadruped  (like a dog   — good starting point)
#                 6 = hexapod    (like an insect — stable, but slower to train)
#               More legs = more joints = bigger neural network = more
#               generations needed. Start with 4.
#
#  thigh_len  — length of the upper leg in metres  (range: 0.3 – 0.6)
#               Longer thighs = bigger stride, but harder to balance.
#
#  shin_len   — length of the lower leg in metres  (range: 0.2 – 0.5)
#               Longer shins = more ground reach, but more likely to collapse.
#
#  hip_range  — how far the thigh can swing forward/backward, in radians
#               (range: 0.5 – 1.2)
#               0.5 = short shuffling steps, 1.2 = very wide strides.
#
#  knee_range — how far the knee can bend, in radians  (range: 0.5 – 1.4)
#               Only bends one way (forward, like a real knee).
#               Higher = can crouch deeper, but risks folding under itself.
#
#  TIPS:
#    - Start with these defaults. They are balanced for a 4-legged walker.
#    - Once your creature walks, try changing one value at a time.
#    - Changing n_legs changes the neural network size — retrain from scratch.

# ══════════════════════════════════════════════════════════════════════
#  STEP 1 — DESIGN YOUR BODY (Maximized Leverages for 35m+ Speed)
# ══════════════════════════════════════════════════════════════════════
BODY = {
    "n_legs":     4,      # 4 legs give immediate balance gradient to optimize velocity 
    "thigh_len":  0.60,   # Maximum allowed length to maximize stride distance 
    "shin_len":   0.45,   # High ground clearance to prevent dragging/snagging 
    "hip_range":  1.20,   # Maximized swing arc arc for explosive ground coverage 
    "knee_range": 1.10,   # Generous knee flex for powerful push-offs
}

CURRENT_GEN = [0] 
# ══════════════════════════════════════════════════════════════════════
#  STEP 2 — WRITE YOUR FITNESS FUNCTION
# ══════════════════════════════════════════════════════════════════════
def my_fitness(data):
    # ── RULE 1: Total exclusion for falling ───────────────────────────
    # A creature that falls must ALWAYS score significantly below upright ones[cite: 77].
    # We maintain a minor distance slope so early messy gens can still learn[cite: 77].
    if data["falls"] > 0:
        return -100.0 * data["falls"] + data["distance"] * 0.1

    # ── RULE 2: High-Velocity Upright Locomotion ──────────────────────
    # Scale distance reward aggressively (x25 instead of x10) to prioritize speed[cite: 46].
    score = data["distance"] * 25.0
    
    # Reward frames spent actively moving forward[cite: 43].
    score += data["step_count"] * 0.15
    
    # Highly reward gait consistency to avoid jerky, wasting energy profiles[cite: 42, 85].
    score += data["smoothness"] * 15.0
    
    # Reward maintaining multiple legs structurally active[cite: 43].
    score += data["legs_active"] * 10.0

    # ── RULE 3: Custom Per-Frame Micro-Penalties ──────────────────────
    # Pull custom metrics using safe dict fetches to prevent script crashes.
    score -= data.get("backward_frames", 0) * 0.5
    score -= data.get("air_frames", 0) * 0.25
    
    # Reward keeping the torso high and proud off the ground to optimize extension.
    avg_height = data.get("accumulated_height", 0) / 600.0
    score += avg_height * 0.1

    return score

# ══════════════════════════════════════════════════════════════════════
#  OPTIONAL — DEFINE YOUR OWN PER-FRAME METRICS
# ══════════════════════════════════════════════════════════════════════
def my_metrics(step_data):
    return {
        # Track and punish frames where the creature slides back or recoils 
        "backward_frames": 1 if step_data["vx"] < -1.0 else 0,

        # Track "bouncing" or "launching". We want a true power-walk, not zero-traction hopping 
        "air_frames": 1 if step_data["feet_down"] == 0 else 0,

        # Track the raw torso height dynamically across all 600 frames
        "accumulated_height": float(step_data["torso_height"]),
    }


# ══════════════════════════════════════════════════════════════════════
#  STEP 2 — WRITE YOUR FITNESS FUNCTION
# ══════════════════════════════════════════════════════════════════════
#
#  This is the most important part. Evolution maximises whatever number
#  you return — so you need to make sure that number actually means
#  "walks far".
#
#  Called once per creature per generation. You receive a data dict
#  with these built-in measurements from the 10-second simulation:
#
#    data["distance"]    — metres travelled forward
#                          This is the main thing to maximise.
#                          Range: 0.0 (didn't move) to ~10.0 (very fast)
#
#    data["falls"]       — how many times the body collapsed
#                          A fall = torso dropped or tilted more than ~40°.
#                          Always penalise this heavily.
#                          Range: 0 (never fell) upward
#
#    data["smoothness"]  — how steady the forward velocity was
#                          1.0 = perfectly smooth, 0.0 = very jerky
#                          Useful if you want an elegant gait, not just fast.
#                          Range: 0.0 – 1.0
#
#    data["step_count"]  — frames where the creature was moving forward
#                          High = actively walking, not just falling forward.
#                          Range: 0 – 600
#
#    data["legs_active"] — fraction of the run where at least HALF the legs
#                          had a foot on the ground at the same time.
#                          1.0 = always properly supported by multiple legs
#                          0.0 = dragging on one leg the whole time
#                          Range: 0.0 – 1.0
#
#  Plus any custom metrics you define in my_metrics() below.
#
#  THE GOLDEN RULE:
#    A creature that falls must ALWAYS score less than one that walks,
#    no matter how far the fallen creature slid. If you break this rule,
#    evolution discovers that falling-and-sliding is an easy shortcut
#    and your creatures will never learn to stand upright.
#
#  HOW NEAT USES THIS NUMBER:
#    NEAT ranks creatures relative to each other. What matters is that
#    better walkers score meaningfully higher than worse ones. If all
#    scores cluster between 9.8 and 10.0, NEAT has almost no signal to
#    work with and progress stalls. Spread your scores out.
  # automatically updated each generation — read-only



# Uncomment this line to disable custom metrics entirely:
# my_metrics = None


# ══════════════════════════════════════════════════════════════════════
#  STEP 3 — PICK YOUR MODE AND GENERATION COUNT
# ══════════════════════════════════════════════════════════════════════
#
#  MODE — what happens when you run:  python bot.py
#
#    "test"     — 5 generations, no visuals. Run this first to confirm
#                 your code has no errors. Takes about 30 seconds.
#
#    "train"    — full training run. Shows a live preview after each
#                 generation. Saves the best genome to best.pkl.
#                 You can stop early — best.pkl is updated every gen.
#
#    "watch"    — loads best.pkl and replays it in a window.
#                 Use this after training to see your creature walk.
#
#    "evaluate" — loads best.pkl, runs 5 trials, prints distance stats.
#                 Use this for a stable measurement of your best result.
#
#  GENERATIONS — how many generations to train for.
#
#    50  gens  ≈  5–10 min   good for testing a new fitness function quickly
#    100 gens  ≈ 15–20 min   default — usually produces a working walker
#    200 gens  ≈ 30–40 min   for a polished, fast gait
#
#  TIP: If your creature still isn't walking after 100 generations, the
#  problem is almost always the fitness function, not the generation count.
#  Revisit Step 2 before running longer.

MODE        = "train"    # start here — switch to "train" once test passes
GENERATIONS = 100


# ══════════════════════════════════════════════════════════════════════
#  NOTHING BELOW THIS LINE NEEDS TO CHANGE
# ══════════════════════════════════════════════════════════════════════

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
        metrics_fn  = my_metrics,
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
        metrics_fn  = my_metrics,
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
        s = arena.evaluate_genome(winner, config, BODY, my_fitness, my_metrics)
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
    from arena.engine import _replay_standalone
    _replay_standalone(winner, config, BODY)

if __name__ == "__main__":
    {"train": mode_train, "test": mode_test,
     "evaluate": mode_evaluate, "watch": mode_watch}.get(
        MODE, lambda: print(f"Unknown MODE '{MODE}'")
    )()
