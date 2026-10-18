# Playbook — house rules

Lessons from real jobs. Each rule has a **why** (what went wrong without it). Claude reads this once per session;
humans should skim it once. Add a rule whenever a client or reviewer corrects something twice.

## Money & generations
1. **Quote cost and get a yes before any paid generation** (Higgsfield, Fal, ElevenLabs, cloud renders).
   State model, count, credits each, total. *Why:* credits run out mid-job and nobody likes surprise bills.
2. **One test shot before a batch.** Review it at full resolution, then batch. *Why:* AI clips fail in ways
   thumbnails hide (warped products, gibberish text, extra limbs).
3. **Trim before you regenerate.** Most bad AI clips have 1–3 good seconds: use `data-media-start`,
   `playback-rate`, a punch-in or a cutaway. *Why:* regenerating is slow and expensive and often no better.
4. **Code shots beat AI shots for UI, type, data and diagrams** — sharper, free, editable.

## Real people & real footage
5. **No generative restoration on real people.** Don't regenerate a real person's voice, don't interpolate
   frames, don't "enhance" faces. Stop at DeepFilterNet noise cleanup, gentle EQ/compression and an honest upscale.
   If a recording is laggy or muffled, say so and suggest B-roll cover or a re-record. *Why:* restored versions
   were judged worse than the authentic source.
6. **Transcribe verbatim, then fix only names and jargon.** Never put words in someone's mouth in captions.

## Ads & clients
7. **Research the category's ads before designing.** Long-running ads in the Meta / TikTok / LinkedIn libraries
   show what works: artifact in the first frame, first-person native feel, numbered steps, demo not claim,
   one segment per ad. *Why:* designs built from brand guides alone looked like templates and were rejected.
8. **Brand guides are identity, not layout.** Take logo, palette, fonts and hard rules (e.g. "artwork never
   animates"); choose layout, length and ratios by what the research says wins.
9. **Casting must match the market.** For Indian audiences (and every specific market) prompt hyper-specific
   regional features, styling and real local settings, phone-real and unretouched. *Why:* generic AI faces read
   as foreign instantly and kill trust.
10. **No fake testimonials, no invented customer numbers.** Claims = product mechanics. Demo data is labelled "Demo".
11. **Cover AI-generated screens with the real product.** Presenters holding phones/laptops show fake UIs.
12. **Never let an image model draw the product, logo or artwork** — composite the real one in.

## Craft
13. **Story + pace beat polish.** A reel of nice scenes with no stakes reads as "basic". Hook in the first second,
    a problem, a twist, a payoff. Cut on the beat; chop cuts every 0.4–0.8 s in hype sections.
14. **Cue sheet first.** Picture, sound and captions share one list of times on a beat grid.
15. **"Edit it like this reference" means exactly like it.** Pull frames at 6 fps over the key moments and write
    down typography, weight pairing, layering (text behind subject via `hyperframes remove-background`),
    placement, motion (blur-in vs bounce) and framing before building. *Why:* impressions from thumbnails were
    "not even 1% close".
16. **Use named moves for real.** When a motion-prompt move is chosen, port its published numbers exactly.
17. **Look before you send.** Snapshot/contact-sheet every render; check captions don't cover eyes/mouth, nothing
    is cropped in 9:16, text contrast passes `hyperframes check`.
18. **Deliver at −14 LUFS**, H.264, 30 fps, named `Title (16x9).mp4` / `(9x16)` / `(4x5)`.
19. **Multi-aspect = re-layout, not crop.** Build every aspect from one source with relative units.

## Repo hygiene
20. **Nothing client-specific in this repo**: no footage, renders, brand assets, transcripts or keys. Work lives
    in `videos/` and `out/` (gitignored). Reusable code goes in a skill or template with placeholders.
21. **Third-party tools are installed from their official sources by `setup.sh`**, not copied in.
