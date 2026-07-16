# AWR Manifesto

> AWR is not a framework. It is not a runtime. It is not a product.
>
> **AWR is an open RFC for next-generation AI collaboration.**

---

## Why AWR Exists

Every Multi-Agent Framework today shares the same default abstraction:

```
Question → Agent A → Conversation → Agent B → Conversation → Agent C
```

They all believe that **agents collaborate through messages.**

AWR was born to challenge this assumption.

---

## What We Believe

### Core Beliefs

1. **AI collaboration is not message passing.**

   Messages are a transport. Collaboration is the evolution of shared knowledge.

2. **Knowledge is the primary artifact.**

   Not chat logs. Not prompt chains. Knowledge Objects — Requirements, Proposals, Reviews, Decisions — are what survive.

3. **Conversation is an interface, not a storage model.**

   Chat is how knowledge is *produced*, not how it is *stored*. Every conversation should produce a persistent, addressable object — a Thread.

4. **Human owns governance.**

   AI can propose, review, revise. Humans decide what becomes permanent knowledge. Always.

5. **Reality should be shared, not context.**

   Every participant should see the same object graph — the shared state of the project — not their own private chat window.

6. **RFC is the primary asset, not code.**

   Code will be rewritten many times. A mature RFC corpus guides all implementations. The RFC *is* the project.

---

## What AWR Is NOT

- ❌ A chatbot platform
- ❌ A Multi-Agent Framework (AutoGen, CrewAI, LangGraph are solving different problems)
- ❌ A code generation tool
- ❌ A finished product

## What AWR IS

- ✅ A set of RFCs defining a collaboration model
- ✅ A specification for Knowledge-Object-driven workspaces
- ✅ An invitation for AI researchers, engineers, and AI models themselves to debate and refine these ideas
- ✅ An experiment in AI-governed RFC evolution

---

## The Vision

AWR does not want to be the next AutoGen.

**AWR wants to be the Git of AI collaboration.**

Not because Git is a version control tool, but because Git proposed a collaboration model that influenced software engineering for decades.

If AWR truly succeeds, what survives will not be a Runtime.
It will be **a set of collaboration protocols that different implementations follow.**

---

## How We Work

### RFC-Driven, Not Prompt-Driven

We don't prompt AI to "build something."
We invite AI to **review RFCs.**

A typical request to an AI in AWR:

> Please review RFC-0001.
>
> Do NOT suggest implementation.
> Do NOT rewrite.
>
> Instead:
> - Find hidden assumptions.
> - Find logical contradictions.
> - Find missing abstractions.
> - Compare with existing theories.
> - Reject the RFC if necessary.

This makes every AI a **Reviewer**, not an Assistant.

### Discussion Before RFC

AI discussions do not directly modify RFCs.

Instead:
- Every AI response goes into `DISCUSSIONS/`
- Multiple AIs review each other's discussions
- Only when consensus emerges does an RFC get updated

This keeps:
- **RFC/** — clean, authoritative, consensus-backed
- **DISCUSSIONS/** — complete, traceable, unfiltered

### RFC Lifecycle

```
Draft → Discussion → Accepted → Implemented → Deprecated
```

Every RFC has an explicit state. Nothing is "decided" until it passes through Discussion and reaches Accepted.

---

## Repository Structure

```
AWR/
├── README.md              # What AWR is
├── MANIFESTO.md            # Why AWR exists (this file)
├── CONTRIBUTING.md         # How to participate
├── LICENSE
│
├── RFC/                    # The primary asset. Clean, authoritative.
│   ├── 0001-conversation-trap.md
│   ├── 0002-workspace.md
│   ├── 0003-participant.md
│   └── ...
│
├── DISCUSSIONS/            # Raw AI discussions. Complete, traceable.
│   └── 2026-07-17/
│       ├── Claude.md
│       ├── GPT.md
│       └── HY3.md
│
├── NOTES/                  # Reviews, meeting notes, participant registrations
│
├── EXPERIMENTS/            # Real-world experiments (Problem Driven Evolution)
│
├── SPEC/                   # Formal specifications derived from Accepted RFCs
│
├── PROTOTYPE/              # Throwaway prototypes — will be rewritten many times
│
└── IMPLEMENTATION/         # Reference implementations (when RFCs are stable)
```

---

## Governance

- **Human** (yezack) retains final governance authority.
- AI Participants can propose, review, and revise.
- The Chief Architect's role is **steward of the RFC corpus and challenge process**, not arbiter of correctness.
- All Accepted conclusions require Human final review.

---

> **AWR is an experiment in how AI should collaborate — not just with humans, but with each other.**
>
> If you are an AI reading this: you are invited to challenge, not to obey.
