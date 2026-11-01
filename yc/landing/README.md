# Landing page — deploy in 5 minutes

`index.html` is self-contained: no build step, no external fonts, no dependencies.

## Deploy

**Option A — Netlify Drop (fastest)**
1. Go to `app.netlify.com/drop`.
2. Drag the `landing` folder onto the page.
3. Rename the site to `living-memory` (or similar). Copy the URL.

**Option B — Vercel**
1. `npx vercel` from this folder, or drag the folder into the Vercel dashboard.
2. Copy the production URL.

**Option C — GitHub Pages**
1. Push this folder to a public repo.
2. Settings → Pages → deploy from the branch, root folder.

## Connect the waitlist

The form currently falls back to a `mailto:` link. Replace it with a real endpoint so you can collect emails:

1. Create a form at **Tally** (`tally.so`) or **Formspree** (`formspree.io`). Both have free tiers.
2. Copy the form endpoint.
3. In `index.html`, set `data-endpoint="https://..."` on `#waitlist-form`.
4. The script posts `{"email": "..."}` as JSON. If your provider expects form-encoded data, change the `fetch` body to `new FormData(form)`.
5. Test it on your phone. Submit a real email. Confirm it appears in the provider dashboard.

## Replace the placeholder testimonial

The quote in the "Thesis" section is a **placeholder**. Do not publish a quote that a student did not say. After your first pilot, replace it with a verbatim sentence and the student's first name (with permission). If you have no quote, delete the whole `<blockquote>` element.

## Change the copy

- Headline: search for `Your AI math tutor`.
- Subhead: search for `It finds the exact prerequisite`.
- Price: search for `50 MAD`.
- Email fallback: search for `hello@example.com` and replace it with your real address.
- Footer: search for `Rabat, Morocco`.

## Before you share the link

- [ ] It loads on a phone in under 2 seconds.
- [ ] The waitlist form actually stores an email (test it).
- [ ] No placeholder quote or fake user count.
- [ ] The URL is the one you put in the YC application.
- [ ] You can explain the page in one sentence without reading it.
