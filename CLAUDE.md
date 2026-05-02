# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the simulation

```bash
pip install -r requrements.txt   # note: filename has a typo

python main.py \
  -d <dataset_path>       # e.g. "Datasets/Non_Identical_FP_vs_+17%_vs_+40%_vs_+50% (medium 25 vs 25 vs 25 vs 25)_1.csv" \
  -p <policy>             # one of: +17%, +20%, +40%, +50%, +60%, +70%, +100%, +200%, all \
  -r <repeat_count>       # number of Monte Carlo iterations (default 20) \
  -m <max_daily_res>      # max reservations per day (default 300) \
  -c <cancel_prob>        # cancellation probability 0–1 (default 0.25) \
  -s <sim_period>         # simulation length in days (default 30) \
  --certified             # enable the FairPlay-certified exposure algorithm
```

Results are written to `Results/<dataset>/<period> days/cancellation probability <p>/<max> max reservations per day/`. Output filenames are prefixed with `Certified___` or `Non-Certified___` depending on the `--certified` flag.

`simpleSimulate.py` is an alternate entry point with the same CLI flags but hardcoded dataset path and cancellation probability; edit the hardcoded values at the top of `__main__` to change them.

**Generate new datasets:**
```bash
cd Datasets && python generator.py
```


## Architecture

This project simulates a hotel booking marketplace to evaluate **FairPlay**, a dynamic pricing policy based on cooperative game theory (Owen Values), against fixed-percentage markup policies (e.g., +17%, +40%, +50%).

### Core pricing concept: Owen Values (`OWEN.py`)

Each day, `computeOwenValues(hotels, day)` builds an **Interaction Similarity Graph (ISG)** over available rooms. Nodes are individual rooms and room-type aggregate nodes; edge weights encode demand pressure (ratio of booked to total rooms). Owen values (a cooperative game theory allocation) are computed from this graph and used as dynamic price increment multipliers for FairPlay hotels. Static-pricing hotels use a fixed percentage increment instead.

### Simulation loop (`Simulation.py`)

Each iteration:
1. Hotels are shuffled and all rooms freed.
2. For each day in the simulation period, `simulate()` is called:
   - A random number of reservations is drawn (higher on weekends/Fridays).
   - For each reservation, Owen values are recomputed for the target check-in date.
   - `__findRoomsToShow()` selects ~30% of available hotels using a **rho-index** (exposure counter / total Owen value) to balance long-run exposure.
   - In **certified mode**, non-FairPlay hotels receive an additional exposure penalty: `beta = min(1, (1 + alpha_CF) / (1 + alpha))`, where `alpha` is the hotel's fixed markup and `alpha_CF` is the FairPlay Owen-value increment for the same room.
   - A user with a randomly sampled budget picks the cheapest available room within budget.
   - Cancellations are probabilistically triggered, with three refund scenarios tracked (non/partial/full).
3. Per-iteration results (income, occupancy rate/share, winning scores, user service rates) are accumulated into DataFrames and written as CSV + plots after each iteration.
4. The full `Simulation` object is pickled to `<output_folder>/<certified_label>_simulation.pkl` after each iteration, allowing resumption via `Simulation.load(file)` and `resume_iterate()`.

### Dataset format

CSVs have columns: `Hotel id, City, Room id, Price, Room Type, Pricing Policy`. Naming convention:
- `Identical_*` — all hotels share the same room configuration.
- `Non_Identical_*` — hotels have independently randomized room configs.
- `(medium 25 vs 25 vs 25 vs 25)` — medium size (50 hotels), split evenly across 4 policies.
- `_N.csv` — one of 10 independently generated random variants.

`Datasets/generator.py` contains helper functions (`manyIdentical`, `manyNonIdentical`, `identical`) to regenerate datasets with different size/policy mix parameters.

### Key constants (`CONSTANTS.py`)

- `PRICING_POLICIES.FAIRPLAY = "fairplay"` — the dynamic Owen-value policy.
- `PRICING_POLICIES.INCREMENT` — maps policy names to their decimal multiplier (e.g., `"+50%"` → `0.5`).
- `PRICING_POLICIES.DEFAULT_POLICIES` — the policies included in aggregate statistics.
- `USER_PROFILES.USER_PROFILES` — maps budget tier names to max nightly price in euros.
- `FEATURES.TYPE` — the only active room feature; values are `single/double/triple/suite`.
