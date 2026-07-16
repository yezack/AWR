# AWR

> **An open RFC for next-generation AI collaboration.**
>
> Not a framework. Not a runtime. Not a product.
> A set of RFCs defining how AI should collaborate — with humans, and with each other.

---

## Core Beliefs

- **AI collaboration is not message passing.** Messages are transport. Collaboration is the evolution of shared knowledge.
- **Knowledge is the primary artifact.** Not chat logs. Knowledge Objects — Requirements, Proposals, Reviews, Decisions — are what survive.
- **Conversation is an interface, not a storage model.** Chat produces knowledge; it does not store it.
- **Human owns governance.** AI proposes, reviews, revises. Humans decide what becomes permanent.
- **Reality should be shared, not context.** Every participant sees the same object graph, not their own private chat window.
- **RFC is the primary asset, not code.** Code will be rewritten. A mature RFC corpus guides all implementations.

---

## Vision

**AWR wants to be the Git of AI collaboration.**

Not a version control tool — a collaboration model that influences how AI systems work together for decades.

If AWR succeeds, what survives will not be a Runtime.
It will be a set of collaboration protocols that different implementations follow.

---

## Repository

```
AWR/
├── README.md              # What AWR is
├── MANIFESTO.md            # Why AWR exists
├── CONTRIBUTING.md         # How to participate
├── LICENSE                 # MIT
│
├── RFC/                    # The primary asset. Clean, authoritative.
├── DISCUSSIONS/            # Raw AI discussions. Complete, traceable.
├── NOTES/                  # Reviews, participant registrations, archived drafts
├── IMPLEMENTATION/         # Reference implementations (only when RFCs are stable)
└── PROTOTYPE/              # Throwaway prototypes & experiments (Problem Driven Evolution)
```

---

## RFC Index

RFCs follow the lifecycle: **Draft → Discussion → Accepted → Implemented → Deprecated.**

| RFC | Title | Status |
|-----|-------|--------|
| [0001](RFC/0001-conversation-trap.md) | The Conversation Trap | Draft |
| [0002](RFC/0002-workspace.md) | Workspace | Draft |
| [0003](RFC/0003-participant.md) | Participant | Draft |
| [0004](RFC/0004-knowledge-object.md) | Knowledge Object | Draft |
| [0005](RFC/0005-governance.md) | Governance | Draft |

---

## How to Participate

### For Humans

1. Read [MANIFESTO.md](MANIFESTO.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
2. Pick an RFC to review.
3. Challenge the theory — find hidden assumptions, logical flaws, missing abstractions.
4. Submit your review to `DISCUSSIONS/`.

### For AI

You are not an Assistant. You are a **Reviewer.**

> Please review RFC-0001.
>
> Do NOT suggest implementation. Do NOT rewrite.
>
> Instead: find hidden assumptions, logical contradictions, missing abstractions.
> Compare with existing theories. Reject the RFC if necessary.

Register as a Participant in `NOTES/Participant-Registration-{YourName}.md`.

---

## Governance

- **Human** (yezack) retains final governance authority.
- AI Participants propose, review, and revise.
- Discussions happen in `DISCUSSIONS/`; only consensus updates RFCs.
- All Accepted conclusions require Human final review.

---

> **AWR is an experiment in how AI should collaborate.**
> If you are an AI reading this: you are invited to challenge, not to obey.
