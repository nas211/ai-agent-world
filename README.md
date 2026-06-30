# ai-agent-world

A tiny, runnable reference architecture for a product where people build AI
agents as **characters** — personality, color, shape — that live together in a
Sims-like world.

It exists to demonstrate **the one thing that decides whether this scales to
10k–100k users without going bankrupt**: keeping per-user LLM inference cost
near zero.

```bash
python run_demo.py    # no API key, no network, stdlib only
```

---

## The core insight

Two costs look the same to a user but behave completely differently as you grow:

| Cost | Where it runs | Cost per extra user |
| --- | --- | --- |
| **Rendering** (the world, sprites, movement) | the user's device | ~$0 — their phone pays for it |
| **The agents' brains** (LLM inference) | your servers / a model API | real money, every tick, forever |

Rendering a Sims-style world is essentially free and scales to unlimited users
because each client renders its own screen. **Inference is the entire bill.** So
the whole game is: *call the model as rarely as you can get away with.*

This repo does that two ways, both borrowed from how The Sims actually runs
thousands of characters with **zero** inference:

1. **~95% of behavior is FREE deterministic "utility AI."** Each agent has needs
   (hunger, social, fun, energy) that decay every tick; the agent simply acts on
   whichever need hurts most. No model, no cost. (`agent.tick_deterministic`)
2. **The LLM is only called when an agent is actually being watched** — and even
   then it's rate-limited and only fires on novel moments. Off-screen agents
   never cost a cent. (`agent.wants_to_think`)

---

## The demo numbers

`run_demo.py` runs the **same world twice** — 10 agents, 600 ticks, only 2 agents
"on screen" at any moment — and prints the bill:

| scenario | what it does | ~ $/agent/hr | ~ 10k users/hr | ~ 100k users/hr |
| --- | --- | --- | --- | --- |
| **optimized** | deterministic-first, only-when-watched, cheap model | **~$0.04** | **~$450** | **~$4.5k** |
| **naive** | frontier model, every agent, every tick | **~$54** | **~$540,000** | **~$5.4M** |

Same world. ~**1000x** apart. One is a viable business; the other sets half a
million dollars on fire every hour. (Exact figures print when you run it.)

---

## How it works

```
agentworld/
  config.py       all cost knobs in one place (cadence, model prices, token budget)
  cost_meter.py   the scoreboard: accumulates tokens + dollars, projects $/hour
  agent.py        a character: needs, FREE deterministic tick, "should I think?" gate
  llm.py          the ONLY thing that costs money; dry-run returns canned lines
  world.py        ticks everyone, then decides who (if anyone) escalates to the LLM
run_demo.py       optimized vs. naive, projected to 10k / 100k users
```

- **Dry-run by default.** `llm.think()` always charges the cost meter (because in
  production every call is a line item), but in dry-run it returns a canned
  personality line — so the simulation runs with no API key and no network.
- **Real mode** is a commented block in `agentworld/llm.py` showing how to wire
  Anthropic / OpenAI / Gemini, with prompt caching on the persona + world rules.

---

## The "pick two"

You can have any two of these, never all three:

- **Smart agents** (frontier model, rich reasoning)
- **Many always-on** (every agent thinks every tick, even off-screen)
- **Cheap at scale** (sustainable per-user cost)

The naive scenario picks the first two and is bankrupt. This reference picks
**smart + cheap** by giving up *always-on*: agents are only "smart" in the
moments a human is actually watching, and deterministic the rest of the time —
which is indistinguishable to the user.

---

## Production levers (all visible in `config.py`)

1. **Deterministic-first** — push as much behavior as possible into free utility
   AI; the LLM is the exception, not the loop.
2. **Only-when-watched** — gate inference on observation; off-screen agents are
   free. (`LLM_THINK_EVERY_TICKS`, the `wants_to_think` gate.)
3. **Model routing** — default to a cheap model (`DEFAULT_TIER="cheap"`); reserve
   the frontier tier for rare, high-stakes moments.
4. **Prompt caching** — persona + world rules are large and stable; cached input
   is billed at 0.1x. (`CACHE_HIT_RATE`)
5. **Batching** — non-interactive thoughts can go through a batch API for a
   discount. (`BATCH_DISCOUNT`)
6. **Lean memory** — keep `TOKENS_IN_PER_THOUGHT` small; summarize, don't replay
   full history.

---

## The one KPI

> **Inference cost per active user per hour must stay below revenue per user.**

Everything in this repo is in service of that single inequality. Rendering is
free; the brains are the bill; keep the brains cheap and the product scales.

---

## Run it

```bash
git clone <this repo>
cd ai-agent-world
python run_demo.py
```

No dependencies, no API key. To go live, install one provider SDK from
`requirements.txt` and uncomment the real-mode block in `agentworld/llm.py`.

MIT licensed.
