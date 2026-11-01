# YC W27 application — draft answers

**How to use this file:** YC changes the form slightly each batch. These are the core questions from the 2026 form. Verify the exact wording and character limits at `ycombinator.com/apply` before you paste anything. Every `[FILL]` is a fact only you can supply. **Do not submit a number you have not measured.** One real user beats ten imaginary ones.

The draft assumes **Path B** (the tutor). If you choose Path A or C, replace the product and traction answers with the variants in `02_pitch_and_one_liners.md`.

---

## Facts to fill before you start

- [ ] Age, nationality, LinkedIn, GitHub, X/Twitter, personal site
- [ ] Current status at EMI: year, expected graduation, student or graduated
- [ ] Full-time start date on this project
- [ ] Incorporation status (almost certainly "not incorporated")
- [ ] Domain and landing page URL
- [ ] Number of classmates who have actually used it (not "will use it")
- [ ] Number of paying users (0 is fine; say 0)
- [ ] Pilot dates and measured results
- [ ] Whether you have a co-founder (if solo, say solo)

---

## Company

### Company name

> **Living Memory**

If the domain is taken, alternatives: `LivingMemory.ai`, `GetLivingMemory.com`, `LivingMemory.app`. Check availability before you print it anywhere.

### Company URL

> `https://[FILL]`

Use the landing page in `landing/index.html`. A URL with a waitlist form is better than a GitHub repo.

### Describe what your company does in 50 characters or less.

> **AI math tutor that remembers your gaps**

(38 characters. Do not add "the" or "an"; the count is tight.)

### What is your company going to make? Please describe your product and what it does or will do.

> Living Memory is an AI math tutor for engineering students. It builds a verified map of what each student knows — every theorem, proof and prerequisite — and remembers every mistake. When a student is stuck, it finds the exact missing prerequisite and teaches that, instead of re-explaining the whole chapter. Repeated mistakes are compacted into one rule, so the tutor gets cheaper and more accurate with use.

**What this answer does:** names the user, the product, the mechanism, and the benefit. It does not mention the paper. That is deliberate.

### Where do you live now, and where would the company be based after YC?

> I live in Rabat, Morocco. The company will be based in San Francisco after YC; I will relocate for the batch and stay if we get traction.

### Explain your decision regarding location.

> My first users are at EMI Rabat, where I study, so Rabat is the right place to build the first version cheaply. San Francisco is where the AI/edtech network, the hiring pool and the YC batch are. I can run the Morocco pilot remotely and be in SF for the batch.

**If you have visa constraints**, say so plainly: "I will need a visa; I will work with YC's team on the timeline." Do not hide it.

### Which batch are you applying for?

> Winter 2027 (January–March 2027), on-time by November 2.

If you cannot start in January, use Early Decision for a later batch. Do not apply for a batch you cannot attend.

---

## Founders

### Founder 1

> **Youssef Zoubir** — [AGE], Moroccan, [EMAIL], [PHONE], [LINKEDIN], [GITHUB], [X].
>
> Engineering student at École Mohammadia d'Ingénieurs (EMI), Rabat. I built the memory engine, the prototype, the evaluation harness and the technical paper solo. Strong in linear algebra, Python and systems; comfortable shipping without frameworks. First startup. [FILL: any internships, teaching, competitive programming, or open-source work.]

### How long have you known each other? How did you meet?

> Solo founder. I have known my first users for [FILL] years at EMI; I am looking for a co-founder with consumer growth or edtech distribution experience, but I would rather ship first than rush a bad match.

**Do not invent a co-founder.** YC funds solo founders; the bar is higher, but a fake or week-old co-founder is worse.

### What is your equity split? Have you incorporated? If not, when will you?

> I own 100%. Not incorporated yet. I will incorporate a Delaware C-corp on acceptance, with YC's standard documents.

### Are you full-time on this? If not, when will you be?

> [FILL — be exact.] I am a [YEAR]-year student at EMI. I am working on Living Memory full-time this semester [or: alongside my final courses], and I will be full-time after [DATE]. If accepted, I will move to San Francisco for the batch.

If you are a student, do not claim to be full-time if you are not. YC will ask. The honest version — "I'm a student, I'm shipping every day, and I'll go full-time on [date]" — is fine.

### Tell us about your background. What are you good at?

> I study engineering at EMI Rabat, one of Morocco's top engineering schools. I am strongest at linear algebra, Python and systems design. I built a local LLM agent with a SQLite memory, a verified dependency graph, retrieval with citations and a human-gated write path — no frameworks, no vector database, no cloud. I also wrote the technical paper describing the mechanism. I learn fast and I ship alone.

### What is the most impressive thing you have built or achieved?

> A memory engine that lets a local 7B model teach itself linear algebra. It stores 52 results and 111 dependency edges, retrieves the relevant ones, cites what it used, and refuses to save anything unverified. It runs on a CPU-only laptop. I built it solo, and wrote the paper that formalizes why consolidation should make memory smaller and more useful.

This is your strongest answer. Keep it concrete: numbers, constraints, solo.

### How did you hear about YC?

> [FILL — be honest: a founder, a blog post, a video, an alum.]

---

## Progress

### How far along are you? How long have you been working on this?

> Working prototype since [DATE]. About 2,600 lines of Python. SQLite for memory, a local Qwen2.5-7B via Ollama, nomic-embed-text for embeddings, numpy for retrieval. 52 seed results, 111 dependency edges, a 10-problem evaluation harness, and a CLI that solves, teaches, saves, cites and consolidates. No external users yet.

**After the sprint**, replace the last sentence with:

> [N] students have signed up; [M] used it at least twice this week; [K] paid 50 MAD. We logged [P] solved problems.

### Do you have users? How many? Revenue? Growth?

**Before the pilot (honest):**

> 0 paying users. 0 external users as of [DATE]. We ran a 10-problem internal evaluation: with memory 8/10 correct vs 9/10 without, at 3× the tokens. That result is why we built compaction — retrieval alone is not enough. Our next milestone is 30 EMI students in a four-week linear-algebra pilot.

**After the pilot:**

> [N] signups, [M] weekly active, [K] paying at 50 MAD/month, [P] problems solved. Retention: [X]% of signups returned in week 2. The first cohort is EMI Rabat's linear algebra course.

Do not round up. "About 30" is worse than "27."

### What is your tech stack?

> Python, SQLite, Ollama (Qwen2.5-7B for reasoning, nomic-embed-text for embeddings), numpy. No web framework yet; the pilot runs through a CLI and a simple web wrapper. CPU-only, local, no cloud dependency. This keeps the cost per answer near zero and the student's data on their machine.

### What are your goals for the next 6 months?

> 1,000 active students at EMI and CPGE Rabat; 100 paying at 50 MAD/month; 40% weekly retention; the consolidation pass live in production; two university partnerships; expansion to Casablanca and Rabat engineering schools. Then MENA.

Pick numbers you believe. If 1,000 is too aggressive, use 500. YC respects a plan you can defend.

### What is the biggest risk to your company? How will you mitigate it?

> Retention. Students try a tutor before an exam and leave after. Mitigation: build around the weekly problem set, not open-ended chat; measure weekly active students, not signups; start with one compulsory course where the pain is weekly. The second risk is platform absorption — OpenAI or Google adds memory. Our answer is the verified map of the student's knowledge and the curriculum, which is not a model feature.

### What do you need most from YC?

> Distribution to the first 10,000 students, hiring help, and the weekly pressure to ship. I can build the engine; I need the network and the pace.

---

## Idea

### Why did you pick this idea? Do you have domain expertise?

> I study engineering at EMI Rabat. I watched classmates memorize proofs for exams and forget them a week later — not because they were lazy, but because the explanation assumed something they never learned. I built the memory engine to diagnose that gap, then wrote the paper because the mechanism is general. Math is the beachhead because a proof can be checked. I am the user, and my first customers are on my campus.

### What is the problem? Why is it important?

> Students do not fail linear algebra because explanations are missing. They fail because the explanation assumes a prerequisite they do not have, and no tutor remembers which one. ChatGPT answers the question and forgets the student. Human tutoring costs 50–150 MAD/hour in Morocco and $50–150/hour in the US, so most students never get diagnosis. The gap is not content; it is memory and verification.

### What is new about what you are making? What substitutes exist today?

> Existing tutors retrieve similar content and explain it again. We maintain a verified dependency graph of the student's knowledge: every claim has a proof, every proof has prerequisites, and the tutor can point to the exact missing node. We refuse to store unverified claims. And we compact: when the same mistake recurs, specific cases are replaced by one general rule, so memory shrinks instead of growing. Substitutes: ChatGPT, Khanmigo, Photomath, Symbolab, YouTube, human tutors.

### Who are your competitors? What do you understand about your business that they don't?

> ChatGPT and Khanmigo are generic chat: they answer well but have no persistent, verified model of the student. Photomath and Symbolab solve steps; they do not diagnose prerequisites. Human tutors are expensive and scarce. Mem0, Zep and Letta sell memory infrastructure to developers; they do not own the student relationship or the curriculum. What we understand: the hard part is not answering math; it is knowing what the student does not know and proving why. Our dependency graph does that, and it gets cheaper as it compacts.

### How do or will you make money? How much could you make?

> Consumer subscription: 50 MAD/month (~$5) in Morocco, $9/month globally, free tier with 5 questions/week. Later, B2B licenses to universities and CPGE schools at $2–5/student/month, and an API for tutoring companies. Bottom-up: roughly 1M Moroccan university students; 1% paying at $60/year = $600K ARR. MENA STEM: roughly 10M students; 1% at $60/year = $6M. Global higher-ed STEM: roughly 200M; 0.5% at $120/year = $120M. Long-term, the memory engine is infrastructure for any high-stakes agent. *(Verify the counts against official EMI/ministry figures before submitting.)*

Label these as illustrative in your own head; if a partner pushes, show the arithmetic. Do not claim a $100B TAM without a bottom-up path.

### How will you get users?

> Start at EMI Rabat: thousands of engineering students, linear algebra is compulsory, and I am on campus. Launch a WhatsApp/Telegram bot and a web app before the next exam period; free for the first 100; measure weekly retention. Then CPGE prep schools, where math is intense and willingness to pay is high. Content-led: solve one hard problem a week on TikTok/YouTube; SEO for "rank nullity," "diagonalization," "injective linear map." The first 30 users come from my own class.

### Why now?

> Two shifts. Open 7B models can now do rigorous linear algebra on a CPU — I run Qwen2.5-7B locally at 5.5 tokens/second, so the marginal cost of an answer is near zero. And students already use AI for homework, but it forgets them; the missing piece is memory plus verification. YC's 2026 Request for Startups lists AI tutoring, and the tooling just became cheap enough for a student in Morocco to ship.

---

## Curious / bonus

### What is something you believe that most people do not?

> Most AI memory will be worthless because it stores unverified text. The winning memory is the one that can prove its claims and compress them. Trust, not recall, is the bottleneck.

### What is the hardest technical problem you have solved?

> Making a 7B model trustworthy enough to write to memory. The model is the easy part. The hard part is the write path: staging, verification, dependency edges, duplicate detection, and compaction, so one wrong answer cannot become infrastructure. I built a human-gated write path and a graph that cites what it used; the next step is automatic verification for the math domain.

### Anything else we should know?

> I am a solo founder from Morocco. I built this on a CPU-only laptop with a local model, no cloud, no funding. The paper is a working draft; the prototype is real. If given the chance, I will out-ship and out-study anyone in the batch.

---

## How to talk about the paper

The paper is a credential, not the pitch. Use it in one clause, never in the first paragraph.

- **In "what's new":** "I wrote the technical paper that formalizes why consolidation makes memory smaller and more useful."
- **If asked for the thesis:** "Memory should consolidate recurring cases into rules, not just append; the prototype implements the mechanism with a human-gated MDL criterion."
- **If asked whether it is published:** "It's a working draft, not peer-reviewed. The prototype is the evidence."
- **Never say:** "The paper proves this works." It proposes a mechanism; the pilot is what tests it.
- **Link:** only if a partner asks. Put the PDF on the landing page or a `/paper` URL, not in the 50-character field.

---

## Before you submit

- [ ] Every `[FILL]` is replaced.
- [ ] No number is invented.
- [ ] The 50-character field is under 50 characters (count it).
- [ ] The one-sentence description can be said without notes.
- [ ] The video is under 60 seconds and shows the product.
- [ ] Someone who does not know the project reads the answers and can explain the company back to you.
- [ ] You submitted on **November 1**, not November 2.
