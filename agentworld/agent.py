"""A character that lives in the world.

The key idea: an agent does almost everything for FREE via deterministic
"utility AI" (exactly how The Sims runs thousands of characters with zero
inference). It only *wants to think* with an LLM when it is being watched AND
enough time has passed AND the moment is novel.
"""

import random

# How fast each need drains per tick. Tuned so agents stay busy without any
# single need dominating.
DECAY = {
    "hunger": 0.8,   # gets hungrier
    "social": 0.6,   # gets lonelier
    "fun": 0.7,      # gets bored
    "energy": 0.5,   # gets tired
}

# The action that satisfies each need (purely cosmetic for the demo).
SATISFY = {
    "hunger": "eat",
    "social": "chat",
    "fun": "play",
    "energy": "sleep",
}


class Agent:
    def __init__(self, name, personality, color, shape):
        self.name = name
        self.personality = personality
        self.color = color
        self.shape = shape

        # Needs run 0..100; lower means more pressing. Start comfortable.
        self.needs = {"hunger": 100.0, "social": 100.0, "fun": 100.0, "energy": 100.0}

        self.ticks_since_llm = 0
        self.last_action = "idle"
        self.last_thought = ""

    # --- The FREE path --------------------------------------------------------

    def tick_deterministic(self):
        """Decay needs and act on the most-pressing one. No LLM, no cost."""
        for need in self.needs:
            self.needs[need] = max(0.0, self.needs[need] - DECAY[need])

        # Pick the lowest need and satisfy it (utility AI: act on what hurts most).
        pressing = min(self.needs, key=self.needs.get)
        self.needs[pressing] = min(100.0, self.needs[pressing] + 40.0)
        self.last_action = SATISFY[pressing]

        self.ticks_since_llm += 1
        return self.last_action

    # --- The decision to spend money ------------------------------------------

    def wants_to_think(self, observed):
        """Should this agent escalate to an LLM this tick?

        Three gates, cheapest first:
          1. Not on screen?            -> no (nobody is watching, don't pay).
          2. Thought too recently?     -> no (rate-limit the expensive path).
          3. Otherwise only sometimes  -> 20%, so only novel moments cost money.
        """
        if not observed:
            return False
        if self.ticks_since_llm < self.LLM_THINK_EVERY_TICKS:
            return False
        return random.random() < 0.2

    # Imported lazily so config stays the single source of truth.
    from .config import LLM_THINK_EVERY_TICKS
