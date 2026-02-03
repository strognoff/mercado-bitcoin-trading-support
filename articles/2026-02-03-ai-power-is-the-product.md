# 2026-02-03 — AI Power Is the Product: Why the Next AI Race Is About Electricity, Cooling, and Governance

AI is having its “industrial moment”. For years, the story was software: bigger models, better data, faster GPUs. Lately the centre of gravity has shifted. The new bottleneck isn’t a clever prompt or a shiny architecture — it’s power, cooling, and the ability to run reliably inside real-world constraints.

If you’ve been watching the tech feed, you can feel it: headlines about **500MW-class data centres**, utilities warning about grid capacity, and ever-louder debates about safety and misuse. The glamour is still there — new models, new features — but the hard part is increasingly physical.

This article is my attempt to say the quiet part out loud:

> In the next few years, the winners in AI won’t just be the teams with the best models. They’ll be the teams who treat energy, infrastructure and governance as first‑class product requirements.

---

## The not-so-secret scale problem

A modern AI stack is brutally simple at a high level:

- compute (chips)
- electricity (to run them)
- cooling (to stop them melting)
- networks (to move data)
- operational discipline (to keep uptime)

For a long time, we pretended the first bullet was everything.

But the second and third bullets are now taking the wheel.

The International Energy Agency (IEA) has been flagging this trend for a while. Their overview of data centres and networks notes that data centres account for roughly **1–1.3% of global final electricity demand** (excluding crypto), and that while efficiency gains have helped, workloads in hyperscale data centres have been growing quickly.

Source: IEA — “Data centres & networks”
https://www.iea.org/energy-system/electricity/data-centres-and-data-transmission-networks

Even if the global percentage sounds small, what matters is concentration:

- Data centres cluster in specific regions.
- Grid upgrades take years.
- Local permitting and public acceptance can be slow.

So a “small” global share can become a serious regional constraint.

---

## Efficiency helps… until it doesn’t

There’s a comforting narrative that goes like this:

> “We’ll get more efficient. Chips improve. Cooling improves. So power won’t matter.”

Efficiency is real — and it’s important — but it’s not a magic eraser.

When demand grows faster than efficiency, total consumption still rises. It’s the same story as video streaming: codecs improved, networks improved, and we still ended up streaming far more.

In AI, the feedback loop is tighter:

- better models → more products
- more products → more users
- more users → more inference
- more inference → more revenue
- more revenue → more training

That loop doesn’t just “tap out” politely.

---

## Cooling is the hidden constraint everyone discovers late

If electricity is the headline constraint, cooling is the constraint you meet at 2am.

Cooling is not just an engineering problem — it’s a *location* problem:

- Can you source enough water (or use air cooling efficiently)?
- Can you build the right heat rejection systems?
- Can you do it without annoying the neighbours?

The point isn’t that it’s impossible. The point is that it’s now part of the competitive game.

If you’re building AI infrastructure and you treat cooling as “someone else’s job”, you’re effectively making your product dependent on an unowned, unmanaged risk.

---

## Governance isn’t paperwork — it’s part of the surface area

The second shift, happening in parallel, is that regulation and safety are moving from “PR concern” to “product surface”.

You can see it in the way policymakers are increasingly framing AI not as an app, but as critical infrastructure:

- questions about harmful content
- questions about misuse
- questions about data handling
- questions about what happens when a model is embedded everywhere

My opinion: **governance is becoming a competitive advantage**.

Not because regulators are always right (they’re not), but because the teams who build robust controls early will ship faster later.

When governance is bolted on after the fact, it turns into a permanent brake.

When it’s designed in, it becomes a steering wheel.

---

## What this means for builders (including small teams)

If you’re not building a hyperscale data centre, you might think none of this matters. I think it matters more than people realise.

### 1) “Compute budgeting” becomes product strategy

Every feature request has a cost:

- latency cost
- token cost
- model cost
- user growth cost

Treat those as first-class, like you’d treat memory usage on mobile.

### 2) Model choice becomes an infrastructure choice

Picking a model isn’t just “quality vs cost”. It’s also:

- operational stability
- vendor reliability
- regional availability
- compliance posture

### 3) The next big differentiator is *systems thinking*

In practice, the best AI products are increasingly the ones that:

- use smaller models where possible
- route requests intelligently
- cache aggressively
- avoid unnecessary inference
- measure everything

The boring stuff wins.

---

## My take: the AI companies that win will look more like utilities

Here’s my slightly spicy opinion:

> The winners of the next AI decade will look less like “apps” and more like “operators”.

They’ll be great at:

- capacity planning
- reliability engineering
- supply-chain strategy
- energy procurement
- governance and audit trails

And that will feel weird, because we’re used to the idea that software is infinitely scalable.

But AI is *not* purely software.

AI is software welded to physics.

If you ignore the physics, you don’t get a magical future — you get outages, cost explosions, and a permanently fragile product.

---

## A practical question to end on

If you’re building with AI right now (product, automation, or tooling), ask yourself:

**What happens if my usage doubles three times?**

- Can I afford it?
- Can I serve it reliably?
- Can I explain the decisions my system makes?

If you can answer those, you’re ahead of most teams.

---

## References

- International Energy Agency (IEA) — Data centres & data transmission networks
  - https://www.iea.org/energy-system/electricity/data-centres-and-data-transmission-networks
- International Energy Agency (IEA) — Electricity 2024 (report overview)
  - https://www.iea.org/reports/electricity-2024
