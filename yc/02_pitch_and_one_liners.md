# Pitch, one-liners, video and demo

Everything in this file is written for **Path B** (the tutor). Variants for Path A and C are at the end. Use the exact wording that feels natural to you; do not read like a press release.

---

## 1. The 50-character field

YC asks: *"Describe what your company does in 50 characters or less."*

Pick one. Character counts include spaces.

| Option | Chars | Notes |
|---|---:|---|
| **AI math tutor that remembers your gaps** | **38** | Recommended. Concrete user + differentiator. |
| A math tutor that never forgets you | 35 | Warmer, slightly less specific. |
| The tutor that remembers your mistakes | 38 | Strong, but "mistakes" can sound negative. |
| Verified memory for AI math tutoring | 36 | More technical; good for Path A/C. |
| The AI tutor that knows your gaps | 33 | Clean, but "knows" is vaguer than "remembers." |
| Memory that makes math stick | 28 | Brandable, less explicit. |

**Use:** `AI math tutor that remembers your gaps`

---

## 2. The "what are you making" description

### 200-character version (for forms, bios, social)

> An AI math tutor that remembers every mistake you make. It finds the exact prerequisite you're missing and compacts repeated mistakes into rules, so it gets cheaper and more accurate with use.

### 500-character version (for the application)

> Living Memory is an AI math tutor for engineering students. It builds a verified map of what you know — every theorem, proof and prerequisite — and remembers every mistake. When you're stuck, it finds the exact missing prerequisite and teaches that, instead of re-explaining the whole chapter. Repeated mistakes are compacted into one rule, so the tutor gets cheaper and more accurate with use. It runs on a local 7B model, so it works offline and costs almost nothing per answer.

### One sentence, spoken

> "We're building an AI math tutor that remembers exactly what you don't know."

---

## 3. The 30-second pitch

> "I'm Youssef, founder of Living Memory. Students don't fail linear algebra because explanations are missing — they fail because the explanation assumes a prerequisite they never learned. ChatGPT answers the question and forgets the student. We build a verified map of what each student knows, find the exact gap, and teach that. We start at EMI Rabat, where I study, and we're onboarding 30 students this month."

**Delivery notes:** say "students don't fail because explanations are missing" slowly; it is the hook. Do not say "memory consolidation" in the first 30 seconds.

---

## 4. The 60-second pitch

> "I'm Youssef, founder of Living Memory. I study engineering at EMI Rabat, and I watched classmates memorize proofs for exams and forget them a week later. The problem isn't a lack of explanations. It's that the explanation assumes a prerequisite they never learned, and no tutor remembers which one.
>
> We built an AI math tutor that keeps a verified map of what each student knows — every theorem, proof and prerequisite. When you get stuck, it finds the exact missing prerequisite and teaches that, instead of re-explaining the whole chapter. And when the same mistake recurs, it compacts the specific cases into one general rule, so the tutor gets cheaper and more accurate with use.
>
> Students pay 50 MAD a month; universities pay per seat. I built the engine and the prototype solo on a CPU-only laptop. We're starting with 30 students at EMI this month, and we're applying to YC because we need distribution and speed, not permission."

**60 seconds is about 150–170 words.** Cut, do not speed up.

---

## 5. The 2-minute pitch

Add these three beats to the 60-second version:

**Why now (20s):**
> "Two things changed. Open 7B models can now do rigorous linear algebra on a CPU — I run Qwen2.5-7B locally at 5.5 tokens per second, so an answer costs almost nothing. And students already use AI for homework, but it forgets them. The missing piece is memory plus verification. YC's 2026 Request for Startups lists AI tutoring; the tooling just became cheap enough for a student in Morocco to build it."

**Competition (20s):**
> "ChatGPT and Khanmigo are generic: they answer well but have no persistent, verified model of the student. Photomath and Symbolab solve steps but don't diagnose prerequisites. Human tutors cost 50–150 MAD an hour and are scarce. Mem0 and Zep sell memory infrastructure to developers; they don't own the student relationship or the curriculum. We win by owning the vertical: the graph, the verifier and the student's history."

**The ask (10s):**
> "We're applying to YC W27. We want distribution to the first 10,000 students, hiring help, and the weekly pressure to ship."

---

## 6. The 1-minute founder video

YC asks for a one-minute video of the founding team. It is not a produced ad. It is a signal: can you explain the company, and are you real?

**Rules:**
- Face on camera for the first 10 seconds, then screen recording of the product.
- Under 60 seconds. Hard stop.
- No music, no slides, no stock footage, no AI voice.
- Say your name and the company in the first sentence.
- Show the product working. If the model is slow, cut the waiting and keep the answer.
- Record on a phone or laptop camera in a quiet room with light on your face.
- Do not read a script with your eyes moving. Put bullet points next to the camera.

**Script (55 seconds):**

| Time | Shot | Words |
|---|---|---|
| 0:00–0:08 | Face | "I'm Youssef Zoubir, founder of Living Memory. We're building an AI math tutor that remembers exactly what you don't know." |
| 0:08–0:20 | Face | "Students don't fail linear algebra because explanations are missing. They fail because the explanation assumes a prerequisite they never learned — and no tutor remembers which one." |
| 0:20–0:40 | Screen: ask a question, show the cited theorem and dependency path | "Our tutor keeps a verified map of what you know. When you're stuck, it finds the exact missing prerequisite and teaches that. It shows you the theorem and the path — it can prove why." |
| 0:40–0:50 | Screen: `/teach`, `/save`, `/stats` | "When you teach it something, it verifies the proof, stores it with its dependencies, and never loses it. Repeated mistakes get compacted into one rule, so memory shrinks as you learn." |
| 0:50–0:58 | Face | "I built this solo at EMI Rabat, where I study. Thirty students start this month. We're applying to YC W27." |

**If you only have 30 seconds**, keep 0:00–0:08, 0:20–0:40 and 0:50–0:58.

---

## 7. The 3-minute demo (for interviews and partners)

Rehearse this until you can do it without looking at notes. Have a backup recording in case the model is slow.

### Setup

- Terminal at large font, dark background, clean prompt.
- `memory.db` seeded (52 nodes, 111 edges).
- Ollama running with `qwen2.5:7b` and `nomic-embed-text`.
- A second terminal tab with `sqlite3 memory.db` open for the graph view (optional).
- The three demo questions typed in a scratch file so you can paste them.

### Script

**0:00 — The promise.**
> "This is a linear algebra tutor with a memory. Watch what happens when I ask it something it wasn't seeded with."

**0:15 — Ask a question it can answer from memory.**
```
What is the rank of [[1, 2], [2, 4]]?
```
Point at the `[context: ...]` and `[cited: ...]` lines.
> "It retrieved five theorems, expanded their dependencies, and cited the two it actually used. Every answer is traceable to the graph."

**0:45 — Teach it something new.**
```
/teach If f: V → W is linear and injective then dim V ≤ dim W :: ker f = {0}, so by rank–nullity dim V = dim im f ≤ dim W
```
> "Nothing is saved yet. The model proposed the dependencies; I approve."

```
/save
```
> "Now it's verified and in the graph. A later question retrieves it."

**1:30 — Ask the question that needs the new theorem.**
```
Is there an injective linear map from R5 to R3?
```
> "It cites the theorem I just taught it. That is accumulation: the tutor got smarter because I used it."

**2:00 — Consolidate (the differentiator).**
Teach two more specific cases of the same idea, then:
```
/consolidate
```
> "It found three near-duplicate examples, proposed one general rule, and checked that the rule is shorter than the cases it replaces. I approve, and memory shrinks instead of growing."

```
/stats
```
> "Same knowledge, fewer nodes. That is the thesis: memory should get smaller and more useful, not just larger."

**2:45 — Close.**
> "We start with linear algebra at EMI Rabat because a proof can be checked. The same engine works anywhere a verifier exists — software tests, industrial incidents, legal precedent. That's the company."

### Failure plan

- **Model is slow:** switch to the recorded video at 0:15; narrate over it.
- **Ollama is down:** show the video and the SQLite graph; do not debug live.
- **The answer is wrong:** say so. "It got that one wrong; here's the trace, and here's why the verifier would reject it." Honesty is a feature.
- **`/consolidate` finds nothing:** explain that the seed is already consolidated; teach two near-duplicate examples live, then run it again.

---

## 8. Words to use and avoid

**Use:** student, prerequisite, gap, proof, verified, traceable, remembers, compacts, cheaper, campus, linear algebra, 50 MAD, 30 students, CPU, local.

**Avoid:** revolutionary, disrupt, leverage, synergy, AGI, "future of education," "personalized learning," "memory layer" (unless asked about infra), "consolidation" (say "compacts"), "graph database" (say "dependency graph"), "LLM" (say "model" or "tutor").

**The grandma test:** if a smart 15-year-old cannot repeat your one-liner after hearing it once, it is too complicated.

---

## 9. Variants for the other paths

### Path A — verified memory for AI agents

- **50 chars:** `Verified memory for AI agents` (29)
- **One-liner:** "Memory that proves it's right."
- **30s:** "AI agents write wrong facts into memory and then build on them. We store every claim as a verified node in a dependency graph, with provenance and confidence, and compact recurring cases into rules. Developers get a memory layer they can audit; enterprises get one they can defend."
- **Honest note:** do not use this for W27 unless you have 3 design partners. Mem0 owns the generic pitch.

### Path C — verified memory for high-stakes agents

- **50 chars:** `Auditable memory for high-stakes AI` (36)
- **One-liner:** "The memory layer for agents that cannot be wrong."
- **30s:** "Banks, hospitals and law firms are deploying agents that cannot afford a wrong fact. We give them a verified dependency graph with provenance, confidence and compaction — every claim traceable, every write approved."
- **Honest note:** strong 12-month story; you need a design partner in one regulated vertical to make it credible.
