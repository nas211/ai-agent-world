"""The only component that actually costs money per user.

`think()` ALWAYS charges the cost meter, because in production every call to a
model is a line item on your bill. In dry-run (the default) it returns a canned
personality line so the entire simulation runs with NO API key and NO network.
"""

import random

from . import config

# Canned lines so dry-run output still feels like characters thinking.
_CANNED = [
    "{name} ({personality}) decides to {action}, humming to themselves.",
    "{name} the {color} {shape} pauses, then goes to {action}.",
    "Feeling {personality}, {name} wanders off to {action}.",
    "{name} glances around the world and chooses to {action}.",
]


class LLM:
    def __init__(self, meter, dry_run=True):
        self.meter = meter
        self.dry_run = dry_run

    def think(self, agent, tier, observed=True):
        """Produce one short thought for an agent and bill the meter.

        The charge happens unconditionally — that is the whole point of the
        demo. What the optimized world controls is *how often this is called*,
        not how much each call costs.
        """
        self.meter.charge(
            tier,
            config.TOKENS_IN_PER_THOUGHT,
            config.TOKENS_OUT_PER_THOUGHT,
            cache_hit_rate=config.CACHE_HIT_RATE,
            batch_discount=config.BATCH_DISCOUNT,
        )

        if self.dry_run:
            template = random.choice(_CANNED)
            thought = template.format(
                name=agent.name,
                personality=agent.personality,
                color=agent.color,
                shape=agent.shape,
                action=agent.last_action,
            )
            agent.ticks_since_llm = 0
            agent.last_thought = thought
            return thought

        # ----------------------------------------------------------------------
        # REAL MODE (commented): wire up an actual provider here. The structure
        # mirrors dry-run — call the model, then the meter already reflects cost.
        # Use prompt caching to make the persona + world rules nearly free.
        #
        # Anthropic (Claude) with prompt caching:
        #   from anthropic import Anthropic
        #   client = Anthropic()
        #   model = "claude-sonnet-4-6" if tier == "frontier" else "claude-haiku-4-5"
        #   resp = client.messages.create(
        #       model=model,
        #       max_tokens=config.TOKENS_OUT_PER_THOUGHT,
        #       system=[{
        #           "type": "text",
        #           "text": persona_and_world_rules,          # large, stable
        #           "cache_control": {"type": "ephemeral"},   # -> billed 0.1x on hits
        #       }],
        #       messages=[{"role": "user", "content": world_snapshot}],
        #   )
        #   thought = resp.content[0].text
        #   # Re-charge using resp.usage for exact accounting:
        #   # self.meter.charge(tier, resp.usage.input_tokens, resp.usage.output_tokens,
        #   #                   cache_hit_rate=..., batch_discount=...)
        #
        # OpenAI:
        #   from openai import OpenAI
        #   client = OpenAI()
        #   resp = client.chat.completions.create(model="gpt-...", messages=[...])
        #
        # Gemini:
        #   import google.generativeai as genai
        #   model = genai.GenerativeModel("gemini-flash-lite")
        #   resp = model.generate_content(prompt)   # supports context caching
        # ----------------------------------------------------------------------

        raise RuntimeError("Real mode not wired up. Run in dry_run=True for the demo.")
