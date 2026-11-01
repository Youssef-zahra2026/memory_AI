# The 16-day sprint — October 17 to November 2

**Goal:** by November 1, you have a working demo, 30 students who have actually used it, 10 who came back, 3 testimonials, 1 payment, and an application that takes 10 minutes to read.

**Rule:** do not build features that do not help you get users or answer a YC question. No auth, no payments integration, no mobile app, no dashboard, no Kubernetes.

---

## The targets (write them on the wall)

| Metric | Target | Why it matters |
|---|---:|---|
| Students who used it at least once | **30** | Proof the product runs for someone other than you |
| Weekly active (used twice in a week) | **10** | The only retention signal you can get in 14 days |
| Paying users | **1** | A payment is a signal; a free signup is a maybe |
| Problems solved and logged | **50** | Your first real dataset |
| Testimonials with a specific sentence | **3** | Evidence the diagnosis works |
| Demo video | **60s** | The application and the interview |
| Benchmark table | **1 page** | With memory vs without; with compaction vs without |

If you hit 5 of 7, apply with confidence. If you hit 2, apply anyway.

---

## Week 1 — build the evidence

### Day 0 — Saturday, October 17: decide and ship the front door

- [ ] Read `01_strategy_memo.md`. Pick Path B. Write the decision in one sentence and do not revisit it this week.
- [ ] Check domain availability: `livingmemory.ai`, `livingmemory.app`, `getlivingmemory.com`. Buy one (≈$10–15/year). If all are taken, use `livingmemory.[your surname].com`; the name matters less than the product.
- [ ] Deploy `yc/landing/index.html` to Vercel or Netlify (drag-and-drop; 5 minutes). Connect a waitlist form (Tally, Formspree, or Google Forms). Test it on your phone.
- [ ] Record a raw 60-second demo on your phone: ask a question, show the cited theorem, teach a theorem, save it, ask the follow-up. Do not edit. Watch it once. Note what is confusing.
- [ ] Write the 50-character description and the one-sentence pitch on a card. Say them out loud 10 times.

**End of day:** a URL you can send to a stranger, and a video you are not ashamed of.

### Day 1 — Sunday, October 18: the first 10 users

- [ ] Write the WhatsApp message (below). Send it to 10 classmates who are currently taking linear algebra. Ask for 20 minutes, not "feedback."
- [ ] Book three in-person sessions: Monday, Tuesday, Wednesday, 5–7pm, one laptop, one quiet room.
- [ ] Prepare the session script: 3 problems of increasing difficulty, one teach-back, one survey.
- [ ] Add a tiny logging file: timestamp, student alias, problem, whether the answer was correct, seconds, whether they said "that's the gap." A CSV is enough.

**Do not** build a web app yet. In-person, one laptop, is faster and gives you more signal.

### Day 2 — Monday, October 19: session 1 (5 students)

- [ ] Run the session. **Do not help.** Watch where they hesitate. Write down the exact words they use when confused.
- [ ] Ask each student to solve one problem with the tutor and one without. Time both.
- [ ] Ask the five questions (below). Record answers in the CSV.
- [ ] At the end: "Would you pay 50 MAD/month for this? If yes, can you pay now?" Take the first payment in cash or bank transfer; record it.

**End of day:** 5 users, 5 data points, 1 list of confusions.

### Day 3 — Tuesday, October 20: fix the one thing

- [ ] Read the confusion list. Pick the **single** most common blocker.
- [ ] Fix only that. Examples: the answer is too long; the citation is unclear; the first token takes 20 seconds; the CLI is scary; the model uses LaTeX.
- [ ] Run session 2 (5 students). Compare: did the blocker disappear?
- [ ] Send the WhatsApp message to 20 more students for the rest of the week.

**Do not** fix everything. One blocker per day.

### Day 4 — Wednesday, October 21: session 3 (5 students) + testimonials

- [ ] Run session 3.
- [ ] Ask for a testimonial in the student's own words: "What did it find that a normal chatbot didn't?" Write it down verbatim. Ask permission to use their first name.
- [ ] Count: signups, weekly active, payments, problems logged.
- [ ] Post one short clip on TikTok/Instagram/WhatsApp status: "I built a tutor that remembers your gaps." Link the landing page.

### Day 5 — Thursday, October 22: 15 more users

- [ ] Run a 30-minute demo in a class or study group (ask a professor or class rep). 15 students, one laptop, 3 problems.
- [ ] Collect 15 signups on the landing page (or a paper sheet if the wifi is bad), then import them.
- [ ] Ask the payment question to everyone. Even a "no" is data.

**End of day:** 25–30 users, 1–3 payments, 30+ problems.

### Day 6 — Friday, October 23: the retention check

- [ ] Message everyone who used it on Monday/Tuesday: "Try this week's problem set; it should know what you missed." Track who returns.
- [ ] Compute week-1 retention: returned / first-time users.
- [ ] Write the one-page benchmark: with memory vs without; with compaction vs without; tokens; seconds; correctness.
- [ ] Update the numbers sheet in `04_interview_prep.md`.

**End of day:** the first honest retention number. If it is low, that is the story: "we learned retention is the problem; here is the fix."

---

## Week 2 — turn evidence into an application

### Day 7 — Saturday, October 24: draft everything

- [ ] Open `03_application_draft.md`. Fill every `[FILL]`.
- [ ] Write the answers in one sitting. Do not edit while writing.
- [ ] Record a 2-minute raw video of yourself answering the 20 interview questions. Watch it once. Note the three worst answers.

### Day 8 — Sunday, October 25: cut 30%

- [ ] Edit every application answer: remove adjectives, add numbers, cut 30% of the words.
- [ ] Read the answers out loud. If you stumble, rewrite the sentence.
- [ ] Ask one friend who does not know the project to read the application and explain the company back to you. If they cannot, rewrite the 50-char and the first paragraph.
- [ ] Record the final 60-second video (script in `02_pitch_and_one_liners.md`). Re-record until it is under 60 seconds and you sound like yourself.

### Day 9 — Monday, October 26: mock interview #1

- [ ] 10 minutes, recorded, friend interrupts every 15 seconds.
- [ ] Score each answer: clear / vague / evasive.
- [ ] Fix the three worst answers. Do not memorize; learn the first sentence and the number.

### Day 10 — Tuesday, October 27: outside eyes

- [ ] Send the application + video to two people: a founder you respect and a YC alum if you can find one (LinkedIn, Twitter, EMI alumni network). Ask for 15 minutes, not a favor.
- [ ] Ask specifically: "What is confusing? What number do you not believe? What would you cut?"
- [ ] Update the numbers sheet. If a number moved, update the application.

### Day 11 — Wednesday, October 28: mock interview #2 + demo rehearsal

- [ ] Mock #2 with a different friend. This time, share your screen and run the demo.
- [ ] Time the demo: 3 minutes maximum. If it runs long, cut the teach step, keep the consolidation step.
- [ ] Record a backup demo video (screen + voice) in case Ollama dies during the real interview.

### Day 12 — Thursday, October 29: final draft

- [ ] Freeze the application. Only fix typos and numbers from now on.
- [ ] Check the 50-character count, the video length, the URL, the email.
- [ ] If everything is ready, **submit today**. Do not wait for a better number that will not arrive.

### Day 13 — Friday, October 30: keep users, not the application

- [ ] Run a fourth session or send the weekly problem set.
- [ ] Collect one more testimonial and one more payment.
- [ ] Do not rewrite the application. It is frozen.

### Day 14 — Saturday, October 31: mock #3 + backup

- [ ] Mock #3, full 10 minutes, no interruptions from you.
- [ ] Test the demo on a fresh terminal, fresh Ollama start, fresh DB.
- [ ] Charge your laptop; test the camera; clean the background.

### Day 15 — Sunday, November 1: submit

- [ ] Final read-through: every `[FILL]` gone, every number measured.
- [ ] Submit by **6:00pm Morocco** (well before the 8:00pm PT deadline, which is ~5:00am Nov 3 Morocco).
- [ ] Screenshot the confirmation. Save the answers as a PDF for your records.
- [ ] Tell your users you applied. Ask them to keep using it.

### Day 16 — Monday, November 2: deadline day

- [ ] Do **not** edit the application. Late edits are how people break working submissions.
- [ ] Keep the product running. If you get an interview, you need the demo alive.
- [ ] Write down what you learned from the sprint: users, retention, the one blocker, the one thing you would build next.

---

## The WhatsApp message (English)

> Hey [Name] — I built a linear algebra tutor that remembers which prerequisite you're missing. I'm testing it with 10 people from our class this week. Can you give me 20 minutes? I'll bring my laptop, you try 3 problems, and I'll shut up and watch. No pitch, no cost. — Youssef

## The WhatsApp message (French)

> Salut [Prénom] — j'ai construit un tuteur de maths qui retient la notion qui te manque. Je le teste avec 10 personnes de la promo cette semaine. Tu peux me donner 20 minutes ? J'apporte mon laptop, tu fais 3 exercices, et je me tais pour observer. Pas de pitch, pas de paiement. — Youssef

## The five questions after each session

1. "What was the moment it helped?" (specific sentence)
2. "What was confusing or slow?"
3. "Did it find a gap you didn't know you had? Which one?"
4. "Would you use this the week before an exam? Why / why not?"
5. "Would you pay 50 MAD/month? If yes, pay now; if no, what would make it worth it?"

Record verbatim answers. Do not paraphrase. Quotes are gold for the application and the interview.

---

## If you fall behind

Triage in this order:

1. **Users beat features.** If you have to choose between fixing the UI and running a session, run the session.
2. **The demo beats the application.** A working 60-second video is worth more than a perfect essay.
3. **One number beats ten adjectives.** If you only get 10 users, say 10.
4. **Submit on time.** A submitted imperfect application beats a perfect one that missed the deadline.

Cut from the plan, in order: the TikTok clip, the second mock interview, the fourth session, the benchmark table. Never cut: the video, the users, the submission.

---

## What you are allowed to say after the sprint

- "30 students used it; 10 came back; 1 paid." (If true.)
- "Retention was low; here is what we learned." (If true.)
- "The model is slow on CPU; here is the latency number." (If true.)
- "We have no users yet; here is the demo and the plan." (If true.)

What you are not allowed to say: "hundreds of users," "revenue," "partnerships," or any number you did not measure. YC will ask for names and dates.
