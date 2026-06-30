"""Central cost knobs for the agent world.

Every number that affects per-user LLM inference cost lives here so the
economics are explicit and tunable in one place. The defaults are chosen to
mirror the demo's headline result: deterministic-first + only-when-watched is
roughly 1000x cheaper than calling a frontier model for every agent every tick.
"""

# --- Simulation cadence -------------------------------------------------------

# Wall-clock seconds represented by a single simulation tick.
TICK_SECONDS = 1.0

# An observed agent is only *allowed* to escalate to the LLM at most once every
# this many ticks. This is the single biggest lever on cost: it caps how often
# the expensive path can fire.
LLM_THINK_EVERY_TICKS = 10


# --- Model catalog ------------------------------------------------------------

# Prices are USD per 1,000,000 tokens (input / output), matching public
# list pricing at the time of writing.
MODELS = {
    "cheap": {
        "name": "gemini-flash-lite",
        "in_per_1m": 0.10,
        "out_per_1m": 0.40,
    },
    "frontier": {
        "name": "claude-sonnet",
        "in_per_1m": 3.00,
        "out_per_1m": 15.00,
    },
}

# Tier used by the optimized path. The cheap model is more than good enough for
# "what does this character do next" once the deterministic layer has already
# handled 95% of behavior.
DEFAULT_TIER = "cheap"


# --- Token budget per LLM "thought" -------------------------------------------

# A single agent "thought" bundles the world snapshot, the agent's persona, and
# recent memory as input, and emits a short action/utterance as output.
TOKENS_IN_PER_THOUGHT = 3000
TOKENS_OUT_PER_THOUGHT = 400


# --- Cost-reduction levers (off by default so the demo shows raw numbers) -----

# Fraction of input tokens served from a prompt cache. Cached input is billed at
# 0.1x. Persona + world rules are highly cacheable in production.
CACHE_HIT_RATE = 0.0

# Fraction discount applied to the final bill when requests are sent through a
# batch API (typically ~0.5 for 50% off). 0.0 means no batching.
BATCH_DISCOUNT = 0.0
