"""Run the SAME world twice and compare the bill.

  optimized -> dry_run, naive=False : deterministic-first, only-when-watched, cheap model
  naive     -> naive=True            : frontier model, every agent, every tick

Needs NO API key and NO network. Just:  python run_demo.py
"""

import random

from agentworld.agent import Agent
from agentworld.world import World

# Seeded so the printed numbers are reproducible run-to-run.
random.seed(7)

N_AGENTS = 10
N_TICKS = 600
ON_SCREEN_PER_TICK = 2   # only this many agents are "watched" at any moment

# A little roster of characters (personality, color, shape).
ROSTER = [
    ("Pixel", "curious", "cyan", "triangle"),
    ("Blob", "lazy", "green", "circle"),
    ("Zap", "hyper", "yellow", "star"),
    ("Mossy", "shy", "olive", "square"),
    ("Ruby", "bold", "red", "diamond"),
    ("Echo", "dreamy", "violet", "hexagon"),
    ("Tofu", "calm", "white", "circle"),
    ("Spark", "playful", "orange", "star"),
    ("Nova", "proud", "blue", "triangle"),
    ("Grit", "stubborn", "gray", "square"),
]


def make_agents():
    return [Agent(*spec) for spec in ROSTER[:N_AGENTS]]


def run(naive):
    agents = make_agents()
    world = World(agents, dry_run=True, naive=naive)
    names = [a.name for a in agents]
    for _ in range(N_TICKS):
        on_screen = random.sample(names, ON_SCREEN_PER_TICK)
        world.step(on_screen)
    return world


def fmt_money(x):
    if x >= 1000:
        return f"${x:,.0f}"
    if x >= 1:
        return f"${x:,.2f}"
    return f"${x:.4f}"


def main():
    optimized = run(naive=False)
    naive = run(naive=True)

    print("=" * 72)
    print("ai-agent-world  —  same world, two brains")
    print(f"{N_AGENTS} agents · {N_TICKS} ticks · {ON_SCREEN_PER_TICK} on screen at a time")
    print("=" * 72)

    rows = []
    for label, world in (("optimized", optimized), ("naive", naive)):
        sim_s = world.sim_seconds()
        world_per_hour = world.meter.per_hour(sim_s)
        per_agent_hour = world_per_hour / N_AGENTS
        rows.append((label, world, per_agent_hour))

        print()
        print(f"[{label}]")
        print(f"  LLM calls         : {world.meter.calls:,}")
        print(f"  tokens (in/out)   : {world.meter.tokens_in:,} / {world.meter.tokens_out:,}")
        print(f"  total spend (sim) : {fmt_money(world.meter.dollars)} over {sim_s:.0f} sim-seconds")
        print(f"  cost / agent / hr : {fmt_money(per_agent_hour)}")

    print()
    print("-" * 72)
    print(f"{'scenario':<12}{'$/agent/hr':>14}{'10k users/hr':>18}{'100k users/hr':>20}")
    print("-" * 72)
    for label, _world, per_agent_hour in rows:
        print(
            f"{label:<12}"
            f"{fmt_money(per_agent_hour):>14}"
            f"{fmt_money(per_agent_hour * 10_000):>18}"
            f"{fmt_money(per_agent_hour * 100_000):>20}"
        )
    print("-" * 72)

    opt = rows[0][2]
    naive_cost = rows[1][2]
    if opt > 0:
        print(f"\noptimized is ~{naive_cost / opt:,.0f}x cheaper than naive — same world.")
    print("Rendering stays client-side (~free). The brains are the bill.")


if __name__ == "__main__":
    main()
