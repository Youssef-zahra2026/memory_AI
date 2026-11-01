# Strategy memo — what to apply as, and why

**Prepared October 17, 2026. Deadline: November 2, 2026, 8:00pm PT.**

This is the file to read before you write any application answer. It is deliberately blunt. The goal is not to make you feel good; it is to give you the strongest possible shot in 16 days.

---

## 1. The uncomfortable truth

YC funds **for-profit companies** that can become very large. It does not fund research projects, papers, or technologies looking for a market.

Right now you have:

- a working prototype (real, solo, CPU-only, local model);
- a technical paper with a clear thesis (real intellectual work);
- a seed memory graph, an evaluation harness, and a 10-problem pilot;
- no external users, no revenue, no co-founder, no incorporation.

That is a strong **founder signal** and a weak **company signal**. YC has funded pre-launch solo founders before, but the application has to make the company obvious in the first 15 seconds. "We wrote a paper about memory consolidation" does not do that. "We built a tutor that remembers exactly what you don't know, and we have 30 students using it" does.

Your job over the next 16 days is not to make the paper better. It is to make the company undeniable.

---

## 2. What YC actually scores

From YC's own materials and thousands of public application teardowns, the partners are reading for five things:

1. **Can you explain what you do in one sentence a smart non-expert understands?**
2. **Is this a huge market, and do you have a wedge into it?**
3. **Why are *you* the person to build this?** (founder–market fit, velocity, evidence you ship)
4. **Is there evidence anyone wants it?** (users, revenue, waitlist, design partners, obsessive usage)
5. **Why now?** (a specific technical or behavioral shift, not a trend)

The paper helps with #3. It does almost nothing for #1, #2, #4, or #5. The application must do those.

---

## 3. Honest scorecard

Scores are illustrative, not scientific. Use them to see where the 16 days should go.

| Dimension | Score (1–10) | Why |
|---|---:|---|
| Founder–market fit | **8** | You are the user: an engineering student at EMI Rabat, strong in linear algebra, built the engine and the paper solo. |
| Technical depth | **8** | A verified dependency graph, retrieval with citations, human-gated writes, local 7B model, evaluation harness. Rare for an applicant. |
| Market size | **7** | Education is huge, but crowded; AI tutoring is a tailwind. Agent memory is bigger but owned by Mem0. |
| Product | **5** | Works, but CLI-only, slow on CPU, no consolidation pass yet, no onboarding. |
| Traction | **1** | No external users. This is the number that must move. |
| Clarity | **6** | The paper is clear; the pitch is currently "memory architecture," which is not a company. |

The sprint in `05_16_day_sprint.md` is designed to move Product to 7 and Traction to 4–5 before November 1. That is the difference between a "maybe" and a real conversation.

---

## 4. The market you are actually in

### The memory-infrastructure market is crowded and well-funded

| Company | What they do | Why it matters to you |
|---|---|---|
| **Mem0** (YC S24) | "The memory layer for AI agents." $24M raised across seed + Series A (Oct 2025), 200K+ developers, ~66K GitHub stars, AWS Agent SDK memory provider. | They own the generic "memory layer" pitch. You cannot out-Mem0 Mem0 in 16 days. |
| **Zep / Graphiti** | Temporal knowledge graph memory for agents; enterprise-oriented. | Graph memory is already a product. |
| **Letta** (formerly MemGPT) | Agent runtime with self-editing memory; ships background "dreaming" (consolidation). | Your consolidation idea is already a feature in a funded competitor. |
| **Cognee, Supermemory, LangMem, Hindsight, Honcho** | Graph/vector memory, profiles, libraries. | More evidence the horizontal layer is a red ocean. |

**Conclusion:** "We built a better memory layer" is not a YC pitch in 2026. Even if your mechanism is better, you would be selling infrastructure to developers against a YC-backed category leader with 200K developers and a $24M war chest.

### The tutoring market is crowded too — but the wedge is different

| Competitor | What they do | What they don't do |
|---|---|---|
| **ChatGPT / Claude** | Answer any math question well. | No persistent, verified model of *this* student. Forgets everything between sessions. |
| **Khanmigo** | AI tutor inside Khan Academy's content and exercises. | Locked to Khan's curriculum; not a diagnosis engine; not an open memory. |
| **Photomath / Symbolab** | Step-by-step solvers. | No memory, no diagnosis, no teaching of prerequisites. |
| **Human tutors** | Personalized, expensive. | 50–150 MAD/hour in Morocco; $50–150/hour in the US. Scarce, inconsistent. |
| **YouTube / textbooks** | Free explanations. | No feedback, no adaptation, no memory. |

**Conclusion:** "AI tutor" alone is crowded. "AI tutor that keeps a verified map of *your* knowledge and finds the exact prerequisite you're missing" is not. The differentiation is the memory + verification, and it is demoable.

---

## 5. Why the memory layer is the wrong application (and the right long-term vision)

Your paper's thesis — memory should consolidate, not just append — is correct and interesting. But as a company:

- **The buyer is a developer**, and developers already have Mem0, Zep, Letta, and their vector database's built-in memory.
- **The value is hard to demo** without a vertical. "Our memory compresses 3 near-duplicates into 1 node" is a feature, not a product.
- **The moat is thin.** A funded competitor can add a consolidation pass in a quarter. Letta already has "dreaming."
- **You have no design partners.** Selling infra requires 5–10 design partners and months of integration work. You have 16 days.

As a **long-term vision**, it is excellent: every high-stakes agent needs a memory it can prove is right. But you earn the right to build that by owning a vertical where the memory is visibly valuable. Math is that vertical because **a proof can be checked**.

---

## 6. The three company stories

### Path A — "Verified memory for AI agents" (horizontal infra)

- **What you sell:** an API/SDK that stores claims as a verified dependency graph, with provenance, confidence and compaction.
- **Buyer:** agent platform teams, enterprises with long-running agents.
- **Pros:** huge ceiling; aligns with the paper; you are technically credible.
- **Cons:** Mem0/Zep/Letta own the category; no design partners; long sales cycles; impossible to validate in 16 days.
- **YC verdict:** weak for W27. Stronger in 6–12 months if you have 3 design partners and a benchmark win.

### Path B — "AI math tutor that remembers you" (vertical, consumer)

- **What you sell:** a subscription tutor for engineering students. It builds a verified map of what each student knows, diagnoses the exact missing prerequisite, and compacts repeated mistakes into rules.
- **Buyer:** students (50 MAD/month in Morocco, $9/month globally), later universities and CPGE schools.
- **Pros:** you are the user; you can reach the first 100 students this week; the demo is magical; the memory engine is a real technical moat; YC's 2026 Request for Startups lists AI tutoring; Morocco/MENA is underserved and cost-advantaged.
- **Cons:** consumer edtech is crowded; retention is hard; "why not ChatGPT?" is the killer question. The answer must be diagnosis + memory, not answers.
- **YC verdict:** strongest available story for W27. It is concrete, demoable, and has a path to a big company.

### Path C — "Verified memory for high-stakes agents" (vertical B2B)

- **What you sell:** a memory/audit layer for finance, legal, healthcare or industrial agents, where a wrong memory is a liability.
- **Buyer:** compliance/engineering teams in regulated industries.
- **Pros:** high willingness to pay; the verification story is strongest; less crowded than generic memory.
- **Cons:** no customers, no domain access, long sales cycles; hard to demo without a vertical.
- **YC verdict:** good 12-month direction, not a 16-day application.

---

## 7. Recommendation

**Apply as Path B, with Path A/C as the vision.**

One sentence:

> **Living Memory is an AI math tutor that remembers every mistake you make — it finds the exact prerequisite you're missing and compacts what you learn into rules.**

The application should make three things obvious:

1. **The user is a student, not a developer.** "I'm an engineering student at EMI Rabat. Linear algebra is compulsory. I built this for my classmates."
2. **The mechanism is the moat.** A verified dependency graph per student + compaction. Not "an AI tutor" — a tutor that *knows what you don't know* and can prove it.
3. **The vision is bigger than tutoring.** "Every high-stakes AI agent needs a memory it can prove is right. We start with math because a proof can be checked."

This lets you be honest about the paper (it is the technical foundation) without asking YC to fund a research project.

---

## 8. The five questions you must answer cold

Write these on one page. Memorize them. Every application answer and interview answer is a variation of one of them.

### Q1. What do you make?

> "An AI math tutor that remembers every mistake you make. It builds a verified map of what you know, finds the exact prerequisite you're missing, and compacts repeated mistakes into rules. Students pay 50 MAD a month."

### Q2. Who pays, and why now?

> "Engineering students in Morocco first — linear algebra is compulsory and tutoring costs 50–150 MAD/hour. Then CPGE prep schools and universities. Why now: open 7B models can do rigorous linear algebra on a CPU, so the marginal cost of a tutor is near zero, and students already use AI for homework but it forgets them."

### Q3. Why won't ChatGPT or Khanmigo do this?

> "They optimize for answering the question. We optimize for knowing the student. ChatGPT has no persistent, verified model of what you've mastered; it re-explains from scratch every time. Khanmigo is locked to Khan's content. Our dependency graph can point to the exact theorem you're missing and show the path — that is a different product."

### Q4. Why won't Mem0 or Zep crush you?

> "They sell memory infrastructure to developers. They don't own the student relationship, the curriculum, or the verifier. If memory becomes a commodity, we still own the vertical and the data about what each student knows. Long-term, our engine can power any high-stakes agent; we earn that by winning math first."

### Q5. Why you?

> "I'm the user. I study engineering at EMI Rabat, I built the memory engine and the paper solo on a CPU-only laptop, and I can reach the first few thousand students on my campus this week. I can also hire engineers in Morocco at a fraction of San Francisco cost."

If any answer takes more than 30 seconds, it is too long.

---

## 9. What "good" looks like on November 1

You do not need 1,000 users. You need **evidence of pull**. Aim for:

- **30 students** signed up from EMI/CPGE.
- **10 weekly active** users (used it at least twice in a week).
- **3 testimonials** with a specific sentence ("it found that I didn't understand rank-nullity, not determinants").
- **1 paying user**, even 20 MAD. A payment is a signal; a free signup is a maybe.
- **50+ solved problems** logged, with correctness and time.
- **A 60-second demo video** that works without you talking over it.
- **A benchmark table**: with memory vs without, with compaction vs without.

If you hit 5 of 7, apply with confidence. If you hit 2, apply anyway — the application is free and the feedback loop is worth it.

---

## 10. What not to do

- **Do not lead with the paper.** "We propose a novel memory architecture" is a research pitch. Lead with the student and the gap.
- **Do not say "no competitors."** It signals you haven't looked. Name ChatGPT, Khanmigo, Photomath, human tutors, and Mem0/Zep for the infra question.
- **Do not call it AGI, "the future of education," or "personalized learning."** Dead words. Say what it does.
- **Do not claim users you don't have.** YC partners will ask for names and numbers. One real user beats ten imaginary ones.
- **Do not recruit a co-founder the week before the deadline.** A bad co-founder is worse than a solo founder. Apply solo and say why.
- **Do not wait until November 2.** Timezone, upload failures, and last-minute edits are real. Submit November 1.
- **Do not hide the pilot result.** "With memory 8/10 vs 9/10 without, at 3× tokens — that's why we built compaction" is a *better* story than pretending retrieval already wins. It shows scientific honesty and explains the product.

---

## 11. The honest odds

Base rate: ~1%. A strong application with a working demo, founder–market fit, and 30 users might be 5–10%. No one can promise more.

But the expected value of applying is high even if you are rejected:

- The 16-day sprint forces you to build the product, talk to users, and sharpen the story.
- YC gives feedback and you can reapply next batch; many funded companies applied more than once.
- The application answers are reusable for other accelerators (a16z speedrun, Techstars, Antler, Flat6Labs, 500 Global).
- If you get an interview, the mock interview and demo practice make you better at every future pitch.

**Apply. Do not quit school or spend money you don't have. Build the company either way.**

---

## 12. Use of funds (if asked)

YC's $500K goes further in Morocco than in San Francisco:

| Item | 18-month budget |
|---|---:|
| 2 engineers (Morocco market) | $80K |
| 1 part-time content/GTM | $30K |
| Compute / API credits | $15K |
| Legal, incorporation, accounting | $15K |
| SF living for 3 months (batch) | $30K |
| User acquisition experiments | $30K |
| Buffer | $50K |
| **Total** | **$250K** |

The remaining $250K is runway. The line that matters: **"$500K buys us 18 months and three engineers in Morocco; the same team in SF would cost 4–5× more."** That is a real advantage, not a sob story.

---

## 13. The one-paragraph version

You are a strong technical founder with a real prototype and a clear thesis, applying into a crowded memory market with no users. The winning move is not to out-Mem0 Mem0; it is to use the memory engine as the moat inside a vertical where it is visibly valuable. Math tutoring is that vertical: you are the user, the first customers are on your campus, a proof can be checked, and the demo shows something ChatGPT cannot do — it knows the exact prerequisite you're missing. Apply as the tutor. Keep the memory engine as the long-term vision. Spend the next 16 days getting 30 students, 10 weekly actives, 3 testimonials, and one payment. Submit November 1.
