"""Accumulates token usage and dollar cost for LLM inference.

This is the scoreboard for the whole demo: the only thing that scales with the
number of users is how many tokens we push through a model and what we pay for
them. Rendering, physics, and deterministic AI never touch this meter.
"""


class CostMeter:
    def __init__(self, models):
        # models: the MODELS dict from config (tier -> pricing).
        self.models = models
        self.tokens_in = 0
        self.tokens_out = 0
        self.dollars = 0.0
        self.calls = 0

    def charge(self, tier, t_in, t_out, cache_hit_rate=0.0, batch_discount=0.0):
        """Bill one LLM call and return its dollar cost.

        Cached input tokens are billed at 0.1x; the resulting line item then has
        the batch discount applied. Output tokens are never cached.
        """
        model = self.models[tier]

        # Split input into cached vs. fresh; cached portion is 10x cheaper.
        cached = t_in * cache_hit_rate
        fresh = t_in - cached
        billable_in = fresh + cached * 0.1

        cost_in = billable_in / 1_000_000 * model["in_per_1m"]
        cost_out = t_out / 1_000_000 * model["out_per_1m"]
        cost = (cost_in + cost_out) * (1.0 - batch_discount)

        self.tokens_in += t_in
        self.tokens_out += t_out
        self.dollars += cost
        self.calls += 1
        return cost

    def per_hour(self, sim_seconds):
        """Project accumulated dollars to an hourly run rate.

        sim_seconds is how much simulated wall-clock the run covered, so this
        turns "we spent $X over N simulated seconds" into "$Y per hour".
        """
        if sim_seconds <= 0:
            return 0.0
        return self.dollars / sim_seconds * 3600.0
