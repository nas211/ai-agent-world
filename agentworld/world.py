"""The world: ticks every agent and decides who, if anyone, gets to think.

Two modes share the exact same agents and deterministic layer:
  * naive=True  -> every agent calls the frontier model every single tick.
  * naive=False -> deterministic-first; only watched, rate-limited, novel
                   moments escalate to the cheap model.
The only difference between them is LLM call volume — which is the bill.
"""

from .cost_meter import CostMeter
from .llm import LLM
from . import config


class World:
    def __init__(self, agents, dry_run=True, naive=False):
        self.agents = agents
        self.naive = naive
        self.meter = CostMeter(config.MODELS)
        self.llm = LLM(self.meter, dry_run=dry_run)
        self.ticks = 0

    def step(self, observed_names):
        """Advance the world one tick.

        observed_names: the set/iterable of agent names currently on someone's
        screen this tick. Off-screen agents never trigger inference.
        """
        observed = set(observed_names)
        self.ticks += 1

        for agent in self.agents:
            # Everyone always runs the free deterministic brain.
            agent.tick_deterministic()

            if self.naive:
                # The expensive baseline: frontier model, every agent, every tick.
                self.llm.think(agent, "frontier", observed=True)
            else:
                # The optimized path: pay only when actually watched + novel.
                is_watched = agent.name in observed
                if agent.wants_to_think(is_watched):
                    self.llm.think(agent, config.DEFAULT_TIER, observed=True)

        return self.meter

    def sim_seconds(self):
        return self.ticks * config.TICK_SECONDS
