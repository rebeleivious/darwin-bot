code1     # ══════════════════════════════════════════════════════════════════════
          #  STEP 1 — MAXIMAL RANGE BODY (DEFAULT SIZE, MAX ANGLES)
          # ══════════════════════════════════════════════════════════════════════
          BODY = {
              "n_legs":     4,      
              "thigh_len":  0.45,   # Kept at default for optimal weight/balance
              "shin_len":   0.38,   # Kept at default to prevent structural collapse
              "hip_range":  1.20,   # ABSOLUTE MAX: Allows massive, sweeping leg drives
              "knee_range": 1.40,   # ABSOLUTE MAX: Allows powerful, deep push-offs
          }
          
          
          # ══════════════════════════════════════════════════════════════════════
          #  STEP 2 — VELOCITY THRESHOLD FITNESS
          # ══════════════════════════════════════════════════════════════════════
          def my_fitness(data):
              # Severe penalty for falling remains critical
              if data["falls"] > 0:
                  return -1000.0 * data["falls"] + data["distance"] * 0.1
          
              # 1. Base Score: Heavy distance priority
              score = data["distance"] * 500.0  
              
              # 2. Exponential Distance Bonus: Magnifies the reward for breaking past 25m up to 35m+
              score += (data["distance"] ** 2.2) * 10.0
          
              # 3. Velocity Threshold Explosion: Massively reward high-speed frames
              score += data["sprint_frames"] * 25.0
              score += data["fwd_speed"] * 2.0
          
              # 4. Fundamental Requirements
              score += data["step_count"] * 1.0
              score += data["legs_active"] * 50.0
          
              # 5. Clean Style Deductions (Additive only, no scaling destruction)
              score -= data["backward_frames"] * 100.0  # Eradicate moving backwards
              score -= data["air_frames"] * 1.0         # Light penalty to discourage chaotic floating
              
              return score
          
          
          # ══════════════════════════════════════════════════════════════════════
          #  OPTIONAL — PER-FRAME METRICS
          # ══════════════════════════════════════════════════════════════════════
          def my_metrics(step_data):
              return {
                  "backward_frames": 1 if step_data["vx"] < -2 else 0,
                  "fwd_speed": step_data["vx"] if step_data["vx"] > 0 else 0,
                  "air_frames": 1 if step_data["feet_down"] == 0 else 0,
                  
                  # SPRINT TRACKER: Identify frames where the creature is moving aggressively fast.
                  # This creates a sharp selection gradient that targets high-momentum actions.
                  "sprint_frames": 1 if step_data["vx"] > 120 else 0,
              }      


code2:       # ══════════════════════════════════════════════════════════════════════
      #  STEP 1 — DESIGN YOUR BODY (HIGH LEVERAGE CYCLING CHASSIS)
      # ══════════════════════════════════════════════════════════════════════
      BODY = {
          "n_legs":     4,      # Quadruped balance base
          "thigh_len":  0.50,   # Increased for a longer stride length
          "shin_len":   0.40,   # Proportional clearance to prevent torso dragging
          "hip_range":  1.10,   # Wide swing arc (max allowed is 1.2) to match high-velocity striding
          "knee_range": 1.10,   # Rigid extension range for powerful forward push-offs
      }
      
      # ══════════════════════════════════════════════════════════════════════
      #  STEP 2 — WRITE YOUR FITNESS FUNCTION (NON-DESTRUCTIVE GRADIENT)
      # ══════════════════════════════════════════════════════════════════════
      def my_fitness(data):
          # Rule 1 Compliance: Fallen structures always sit below upright ones.
          if data["falls"] > 0:
              return -500.0 * data["falls"] + data["distance"] * 0.1
      
          # Golden Rule Anti-Flat Population Bonus: Standing upright guarantees a solid 
          # base score, preventing random search stalling in Generation 1.
          score = 100.0 
      
          # Primary Driver: Steep linear distance scaling (25m = 1250 pts | 35m = 1750 pts)
          score += data["distance"] * 50.0
      
          # Secondary Driver: Kinetic Progress Filter (Custom Metric)
          # Exponentially rewards high-speed frames to select for aggressive running gaits
          score += data["velocity_drive"] * 2.5
      
          # Target Requirement: Balanced scaling rewards clear forward stepping over sliding
          score += data["step_count"] * 0.5
          score += data["legs_active"] * 30.0  
      
          # Style Adjustments: ADDITIVE ONLY to ensure top speed is never throttled
          score += data["smoothness"] * 40.0
          score -= data["backward_frames"] * 50.0  # Eradicate moving backwards
      
          return score
      
      # ══════════════════════════════════════════════════════════════════════
      #  STEP 3 — DEFINE CUSTOM PER-FRAME VELOCITY METRICS
      # ══════════════════════════════════════════════════════════════════════
      def my_metrics(step_data):
          vx = step_data["vx"]
          
          return {
              # Catch reverse motion frames immediately
              "backward_frames": 1 if vx < -2 else 0,
              
              # VELOCITY DRIVE: Evaluates how fast the creature runs per frame.
              # Squaring the velocity gives an immense mathematical boost to fast 
              # actions, forcing NEAT to select for explosive velocity changes.
              "velocity_drive": ((vx / 10.0) ** 2) if vx > 0 else 0,
          }
      
      MODE        = "train"    # Set to train
      GENERATIONS = 100        # Run the full baseline generation suite
