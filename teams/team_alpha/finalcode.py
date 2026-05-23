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
#  STEP 1 — DESIGN YOUR BODY (OPTIMIZED FOR HIGH STRIDE VELOCITY)
# ══════════════════════════════════════════════════════════════════════
BODY = {
    "n_legs":     4,      # Quadruped baseline stability
    "thigh_len":  0.50,   # Increased leverage length for a wider stride
    "shin_len":   0.40,   # Balanced ground reach clearance
    "hip_range":  1.10,   # Open swing arc for massive forward lunges
    "knee_range": 1.10,   # Rigid extension for powerful push-offs
}
CURRENT_GEN = [0]

def my_fitness(data):
    # Rule 1 Compliance: Fallen structures always score below upright ones.
    if data["falls"] > 0:
        return -1000.0 * data["falls"] + data["distance"] * 0.1

    # Golden Rule Anti-Flat Bonus: Standing upright ensures a baseline survival score.
    # This prevents random search stall in Generation 1.
    score = 100.0 

    # EXPONENTIAL DISTANCE SCALING:
    # 20m = 400 pts | 26m = 676 pts | 35m = 1225 pts.
    # This steep curve forces the network to prioritize distance maximization.
    score += (data["distance"] ** 2) * 1.5

    # SPEED REWARD INTEGRATION:
    # Heavily reward high-velocity frames and elite sprint breakthroughs
    score += data["velocity_drive"] * 2.0
    score += data["sprint_frames"] * 15.0

    # DOWNSCALE PASSIVE FRAME FILLERS:
    # Reduce the weight of passive survival metrics so they don't flatten the pool
    score += data["step_count"] * 0.2
    score += data["legs_active"] * 10.0  

    # STYLE MODIFIERS:
    # Additive only. This ensures top speed is never throttled by a multiplier.
    score += data["smoothness"] * 30.0
    score -= data["backward_frames"] * 100.0  # Eliminate backtracking completely

    return score

# ══════════════════════════════════════════════════════════════════════
#  STEP 3 — DEFINE CUSTOM PER-FRAME VELOCITY METRICS
# ══════════════════════════════════════════════════════════════════════
def my_metrics(step_data):
    vx = step_data["vx"]
    
    return {
        # Identify and punish reverse motion immediately
        "backward_frames": 1 if vx < -2 else 0,
        
        # VELOCITY DRIVE: Evaluates how fast the creature runs per frame.
        # Squaring the velocity gives an immense mathematical boost to fast 
        # actions, forcing NEAT to select for explosive velocity changes.
        "velocity_drive": ((vx / 10.0) ** 2) if vx > 0 else 0,
        
        # SPRINT TRACKER: Explicit bonus for breaking past competitive speeds
        "sprint_frames": 1 if vx > 150 else 0,
    }

# Execution state verification
MODE        = "train"    
GENERATIONS = 200


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
