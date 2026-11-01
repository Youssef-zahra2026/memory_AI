# Optional 10-slide deck

YC does **not** require a deck. The application is the form and the video; the interview is a conversation. Use this only if an investor, partner, or advisor asks for one, or if you need a visual for a demo day.

**Design rules:** one idea per slide, one number per slide, no walls of text. 16:9. Dark background, one accent color. Font large enough to read on a phone. No stock photos of students. Screenshots of the real product beat illustrations.

---

## Slide 1 — Title

**Living Memory**
*An AI math tutor that remembers your gaps.*

Youssef Zoubir — Founder
[email] · [URL]

> **Speaker note:** "I'm Youssef. We're building an AI math tutor that remembers exactly what you don't know."

---

## Slide 2 — The problem

**Students don't fail because explanations are missing. They fail because the explanation assumes a prerequisite they never learned.**

- ChatGPT answers the question, then forgets the student.
- Human tutoring costs 50–150 MAD/hour in Morocco; most students never get diagnosis.
- The gap is not content. It is **memory** and **verification**.

> **Speaker note:** Tell the story of one classmate. Name the theorem they missed. Make it concrete.

---

## Slide 3 — The insight

**A tutor should remember a *graph*, not a chat history.**

Every theorem depends on other theorems. If you know which node is missing, you know what to teach.

- Verified nodes, not unverified text
- Dependency edges, not a flat log
- Compaction, not endless appending

> **Speaker note:** "This is the difference between a chatbot with history and a tutor that knows you."

---

## Slide 4 — The product

**Ask → retrieve → diagnose → teach → verify → compact**

1. Student asks a question.
2. Tutor retrieves the relevant theorems and their dependencies.
3. It cites what it used and points to the missing prerequisite.
4. Student teaches or approves a new result; it is stored with edges.
5. Repeated cases are compacted into one rule.

> **Speaker note:** Walk left to right. Do not explain the database schema.

---

## Slide 5 — Demo

**Three screenshots (or a 30-second embedded video):**

1. A question with `[context: ...]` and `[cited: ...]` — traceability.
2. A taught theorem saved with its dependency edges — accumulation.
3. `/consolidate` before/after: 3 nodes → 1, same knowledge — compression.

> **Speaker note:** "This is the whole thesis in one screen: the memory got smaller and the answer got more specific."

---

## Slide 6 — Why now

**The marginal cost of a rigorous tutor just fell to near zero.**

- Qwen2.5-7B runs on a CPU laptop at ~5.5 tokens/sec; no cloud bill.
- Students already use AI for homework, but it forgets them.
- YC's 2026 Request for Startups lists AI tutoring.

> **Speaker note:** "A student in Morocco can now run a tutor that would have needed a data center five years ago."

---

## Slide 7 — Market

**Start with one compulsory course. Expand by geography and stakes.**

| Layer | Size | Revenue at 1% penetration |
|---|---:|---:|
| Moroccan university students | ~1M | $600K ARR at $60/yr |
| MENA STEM students | ~10M | $6M ARR at $60/yr |
| Global higher-ed STEM | ~200M | $120M ARR at $120/yr |

*Illustrative bottom-up arithmetic. Verify the counts against official figures before a partner meeting.*

Long-term: verified memory for any high-stakes agent (software, legal, industrial).

> **Speaker note:** "These are bottom-up, not a top-down TAM. One percent of one million students is a real business before we leave Morocco."

---

## Slide 8 — Business model

**Students pay monthly. Universities pay per seat. The engine is the moat.**

- Consumer: 50 MAD/month (~$5) in Morocco; $9/month globally; free tier 5 questions/week.
- B2B: $2–5/student/month for universities and CPGE schools.
- Later: API for tutoring companies.
- Gross margin positive from day one because inference is local.

> **Speaker note:** "The first paying user is a student, not a university. That keeps the feedback loop short."

---

## Slide 9 — Competition

|  | Answers | Remembers you | Verifies | Diagnoses the gap |
|---|:---:|:---:|:---:|:---:|
| ChatGPT / Khanmigo | ✓ | — | — | — |
| Photomath / Symbolab | ✓ | — | — | — |
| Human tutor | ✓ | ✓ | ✓ | ✓ (expensive) |
| Mem0 / Zep (infra) | — | ✓ (for developers) | partial | — |
| **Living Memory** | ✓ | ✓ | ✓ | ✓ |

> **Speaker note:** "Everyone answers. Nobody remembers *and* verifies *and* diagnoses at a student price. That intersection is the company."

---

## Slide 10 — Traction, team, ask

**Traction:** [N] students, [M] weekly active, [K] paying, [P] problems solved, [X]% week-2 retention.

**Team:** Youssef Zoubir, founder. Engineering at EMI Rabat. Built the engine, prototype and paper solo.

**Ask:** YC W27. $500K for 18 months, two engineers and one growth hire in Morocco.

> **Speaker note:** End on the number, not the vision. "Thirty students, ten weekly active, one paying. We start with linear algebra because a proof can be checked."

---

## What not to put in the deck

- A timeline of the field since 1950.
- A architecture diagram with 14 boxes.
- "We have no competition."
- A TAM bubble chart with no bottom-up arithmetic.
- A team slide with advisors you have not asked.
- More than 10 slides.

## If you have 60 seconds and one slide

Use Slide 2 + Slide 5. Problem, then demo. That is the whole pitch.
