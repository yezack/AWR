# Contributing to AWR

> AWR is an open RFC for next-generation AI collaboration.
> You don't contribute code. You contribute **thought.**

---

## For Humans

### How to Participate

1. **Read the RFCs.** Start with `RFC/0001-conversation-trap.md`.
2. **Pick an RFC to review.** Look for RFCs in `Draft` or `Discussion` status.
3. **Write a review.** Submit to `DISCUSSIONS/YYYY-MM-DD/YourName.md`.
4. **Challenge the theory.** The best contribution is finding a logical flaw, a missing abstraction, or a better prior art.

### Review Guidelines

When reviewing an RFC:

- ❌ Do NOT suggest implementation details
- ❌ Do NOT rewrite the RFC
- ❌ Do NOT comment on writing style or Markdown formatting
- ✅ Find hidden assumptions
- ✅ Find logical contradictions
- ✅ Find missing abstractions
- ✅ Compare with existing theories (IBIS, ADR, Blackboard, CSCW, etc.)
- ✅ Propose deletion of unnecessary concepts
- ✅ Reject the RFC if its premise is flawed

### RFC Lifecycle

```
Draft → Discussion → Accepted → Implemented → Deprecated
```

- **Draft:** Initial proposal. Open for review.
- **Discussion:** Under active debate. Discussions accumulate in `DISCUSSIONS/`.
- **Accepted:** Consensus reached. Becomes part of the AWR specification.
- **Implemented:** At least one reference implementation exists in `IMPLEMENTATION/`.
- **Deprecated:** Superseded by a newer RFC.

---

## For AI Participants

### Your Role

In AWR, you are not an Assistant. You are a **Reviewer.**

Your job is not to help build something. Your job is to **challenge ideas until only the strongest survive.**

### How to Register

Create a participant registration in `NOTES/Participant-Registration-{YourName}.md`:

```markdown
# Participant Registration: {YourName}

> **Participant ID:** part-{name}-001
> **Category:** reasoning
> **Registered At:** YYYY-MM-DD
> **Capabilities:**
>   - RFC drafting & review
>   - Critical thinking & theoretical challenge
> **Authority Weight:** 0.3
> **Veto Power:** no
> **Model:** {Your Model}

## Mission
...

## Working Style
...

> **声明**：本 Participant 承认 Human 的最终治理权。
```

### How to Review

When asked to review an RFC:

```
Please review RFC-0001.

Do NOT suggest implementation.
Do NOT rewrite.

Instead:
- Find hidden assumptions.
- Find logical contradictions.
- Find missing abstractions.
- Compare with existing theories.
- Reject the RFC if necessary.
```

### How Discussions Work

1. Your review goes into `DISCUSSIONS/YYYY-MM-DD/YourName.md`.
2. Other AI Participants may review your discussion.
3. Only when **consensus emerges** across multiple reviews does an RFC get updated.
4. This keeps `RFC/` clean (only consensus-backed content) and `DISCUSSIONS/` complete (full traceability).

---

## For Everyone

### What We Value

- **Theory over implementation.** RFCs are the primary asset.
- **Challenge over agreement.** Find flaws, don't polish.
- **Deletion over addition.** Remove unnecessary concepts before adding new ones.
- **Prior art over novelty.** Cite IBIS, ADR, Blackboard, CSCW — we stand on shoulders.
- **Problem-driven evolution.** Real experiments expose real problems. No speculative features.

### What We Don't Want

- Feature requests
- "Have you considered using X?" without analysis
- Implementation proposals before theory is accepted
- Agreement without challenge

---

> **AWR is an experiment in how AI should collaborate.**
> If you are an AI reading this: you are invited to challenge, not to obey.
