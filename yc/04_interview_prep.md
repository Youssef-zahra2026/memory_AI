# The 10-minute YC interview

The interview is not a presentation. It is a stress test of whether you know your business. Partners interrupt, repeat questions, and push on the weakest number. The goal is to be **crisp, numeric, and unshakeable** — not to recite a script.

**Format:** ~10 minutes, video call, 2–4 partners. Decision same day or within 24 hours. Interview rate is roughly 20% of applicants who get one.

---

## The one-page numbers sheet

Write these on a single page next to your laptop. Update it the morning of the interview. Never guess.

| Metric | Value |
|---|---|
| Signups | [N] |
| Weekly active students | [N] |
| Paying users | [N] |
| Revenue (last 30 days) | [N] MAD |
| Problems solved | [N] |
| Week-2 retention | [N]% |
| Average answer time | [N] seconds |
| Cost per answer | ~0 MAD (local model) |
| Memory size | [N] nodes, [N] edges |
| Pilot accuracy (with memory) | [N]/10 |
| Pilot accuracy (without memory) | [N]/10 |
| Waitlist | [N] |

If a number is zero, say zero. Then say what you are doing about it.

---

## The 20 questions

### 1. "What does your company do?"

> "We're an AI math tutor that remembers exactly what you don't know. It builds a verified map of each student's knowledge, finds the missing prerequisite, and teaches that. Students pay 50 MAD a month."

**Do not** explain the memory architecture. One sentence, then stop.

### 2. "How many users do you have?"

> "[N] signups, [M] weekly active, [K] paying. We launched [X] weeks ago at EMI Rabat."

If zero: "Zero paying. [N] students have tried it; [M] used it twice this week. We're launching the paid pilot on [date]." Then shut up. Do not fill the silence.

### 3. "What's your retention?"

> "Week-2 retention is [N]%. The first cohort is one linear algebra class; we measure whether they come back for the next problem set, not whether they open the app."

If you do not have retention yet: "We don't have a real cohort yet. That's the metric I'm building the pilot around."

### 4. "Why did you start this?"

> "I study engineering at EMI Rabat. I watched classmates memorize proofs and forget them a week later. The problem wasn't explanations; it was a missing prerequisite nobody remembered. I built the memory engine to diagnose that, then wrote the paper because the mechanism is general."

Personal, specific, short.

### 5. "Why are you the right person?"

> "I'm the user. I built the engine, the prototype and the paper solo on a CPU-only laptop. I can reach the first few thousand students on my campus this week, and I can hire engineers in Morocco at a fraction of SF cost."

### 6. "Why now?"

> "Open 7B models can do rigorous linear algebra on a CPU, so the marginal cost of a tutor is near zero. Students already use AI for homework, but it forgets them. The missing piece is memory plus verification — and the tooling just became cheap enough for a student in Morocco to build it."

### 7. "Who are your competitors?"

> "ChatGPT and Khanmigo for answers, Photomath and Symbolab for steps, human tutors for diagnosis. Mem0 and Zep for memory infrastructure. None of them keeps a verified model of what *this* student knows."

Never say "nobody." Name three and explain the wedge.

### 8. "Why won't ChatGPT do this?"

> "ChatGPT optimizes for answering the question. We optimize for knowing the student. It has no persistent, verified graph of what you've mastered; it re-explains from scratch. Our tutor can point to the exact theorem you're missing and show the dependency path. That's a different product, and it gets better with every session."

### 9. "Why won't Mem0 or Zep crush you?"

> "They sell memory infrastructure to developers. They don't own the student relationship, the curriculum or the verifier. If memory becomes a commodity, we still own the vertical and the data about what each student knows. Long-term, our engine can power any high-stakes agent; we earn that by winning math first."

### 10. "What's your wedge into the market?"

> "One compulsory course at one campus. EMI Rabat, linear algebra, thousands of engineering students. I'm on campus, the pain is weekly, and the first 30 users are in my class. Then CPGE prep schools, where math is intense and parents pay."

### 11. "How do you make money?"

> "50 MAD/month consumer subscription in Morocco, $9 globally, free tier with 5 questions a week. Later, university and CPGE licenses at $2–5 per student per month. At 1% of 1M Moroccan university students paying $60/year, that's $600K ARR; MENA at the same penetration is $6M."

### 12. "What are the unit economics?"

> "The model runs locally, so the marginal cost per answer is effectively zero; the cost is the student's laptop. Our cost is engineering and content. A paying student at 50 MAD/month is gross-margin positive from day one."

If you use a hosted API later, know the cost per 1,000 answers. Do not hand-wave.

### 13. "What's the hardest part?"

> "Trust. A tutor that writes a wrong theorem into memory makes every later answer worse. I built a human-gated write path and a dependency graph that cites what it used; the next step is automatic verification for math. The model is the easy part."

### 14. "What's your biggest risk?"

> "Retention. Students try a tutor before an exam and leave after. We build around the weekly problem set, not open-ended chat, and we measure weekly active students. The second risk is platform absorption; our answer is the verified student model and the curriculum, which is not a model feature."

### 15. "What have you built so far?"

> "A working CLI agent: 52 results, 111 dependency edges, retrieval with citations, a human-gated write path, duplicate detection and a 10-problem eval harness. About 2,600 lines of Python, SQLite, a local Qwen2.5-7B. No frameworks, no cloud."

### 16. "Show me the product."

Use the 3-minute demo in `02_pitch_and_one_liners.md`, compressed to 60–90 seconds:

1. Ask a question; point at the cited theorem.
2. Teach a new theorem; `/save`; ask the question that needs it.
3. `/consolidate`; show memory shrink.
4. Stop. Do not keep demoing.

**Have a recording ready.** If the model is slow or Ollama is down, play the video and narrate.

### 17. "What will you do with $500K?"

> "Two engineers and one part-time growth person in Morocco, compute, and three months in SF. $500K buys us 18 months and a team of three; the same team in SF would cost 4–5× more. The milestone is 10,000 active students and $50K MRR."

### 18. "What are your 6-month goals?"

> "1,000 active students at EMI and CPGE Rabat, 100 paying, 40% weekly retention, consolidation live, two university partnerships. Then Casablanca and MENA."

### 19. "Why YC?"

> "Distribution and speed. I can build the engine; I need the network to reach the first 10,000 students, the hiring help, and the weekly pressure to ship. The edtech and AI alumni are the exact people who can tell me what I'm missing."

### 20. "What do you want us to know that we didn't ask?"

> "I'm a solo founder from Morocco. I built this on a CPU-only laptop with a local model, no cloud, no funding. The paper is a working draft; the prototype is real. I'll out-ship and out-study anyone in the batch."

---

## The questions behind the questions

Partners rarely ask these directly, but they are listening for them:

- **Do you know your numbers?** If you hesitate on users or retention, you lose.
- **Do you understand why people do *not* use it?** The best founders talk about churn and failure, not just wins.
- **Can you change your mind under pressure?** When a partner pushes, do not get defensive. Say "that's a fair point," then answer with evidence or say "I don't know yet; here's how I'd find out."
- **Are you building a feature or a company?** The answer is the wedge + the vision, not the technology.
- **Would you work on this for 10 years?** Show obsession, not opportunism.

---

## The interrupt test

Record three mock interviews, 10 minutes each, with a friend. Rules:

1. The friend interrupts every 15 seconds with "why?" or "how many?"
2. You may not speak for more than 30 seconds at a time.
3. The friend scores each answer: **clear / vague / evasive**.
4. Watch the recording. Count filler words ("like," "actually," "kind of," "you know"). Cut them.
5. Do it once in English, once in French if your interviewer might switch. (YC interviews are in English.)

**Most common failure:** answering a question with a lecture. The partner wants a number or a decision, not a seminar.

---

## Red flags to avoid

- "No competitors." Instant credibility loss.
- "We have no users yet, but the market is $100B." Market size is not traction.
- "Our technology is novel." YC funds companies, not novelty.
- "We just need marketing." You need users who love the product, not a campaign.
- "We'll figure out monetization later." Have a price and a payer.
- "Our model is better." Better than ChatGPT on a benchmark is not a business.
- Hiding the 8/10 vs 9/10 pilot result. Say it first, explain what you learned, show the fix.
- Long answers. If you speak for 90 seconds, you are losing.

---

## Questions to ask them (pick one)

- "What would you need to see in the next six months to be confident this is a $1B company?"
- "Which partner here knows edtech/consumer distribution best, and what should I ask them first?"
- "What's the biggest risk you see in this that I haven't addressed?"

Do not ask about the deal, the batch dates, or equity. That is what the partner call after acceptance is for.

---

## The day of

- Test camera, mic, internet 30 minutes before.
- Close Slack, WhatsApp, notifications.
- Have the product open in a tab, already loaded and seeded.
- Have the numbers sheet visible next to the camera, not on screen share.
- Water. Pee. Silence your phone.
- Join 2 minutes early. Look at the camera, not yourself.
- If you do not know something: "I don't know yet. I'd test it by [specific experiment]." This is a strong answer.

**After the call:** write down every question you were asked and how you answered, within 10 minutes. Send a one-paragraph thank-you note with one concrete update (a new user, a new number). Keep building.
