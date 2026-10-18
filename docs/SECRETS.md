# Keys & accounts

**No key, token or password ever goes in this repo.** Each person connects their own accounts. Everything
except AI generation works with no accounts at all (code shots, synth music, Kokoro voice, captions).

| Service | Needed for | How to connect |
|---|---|---|
| Higgsfield | AI images/video (launch-film AI shots, UGC presenters) | Claude app → Settings → Connectors → add Higgsfield and sign in. Check balance by asking Claude "what's my Higgsfield balance?" |
| Fal | Music-video plugin | Get a key at fal.ai → in a terminal: `claude plugin configure motion-graphics-music-video@makevoid-music-video` and paste it when asked. Restart the app. |
| Apify | Ad Library research | Claude app → Connectors → Apify (or skip; Claude can research ads in the browser) |
| ElevenLabs (via Higgsfield) | Premium/cloned voices | Comes with Higgsfield |

If the music-video plugin shows "Connection closed": Homebrew Ruby isn't on the app's PATH. Run
`setup/setup.sh --only plugins --add-path`, then fully quit and reopen the Claude app.

Before a paid generation Claude must state the model, count and total cost and wait for your yes (PLAYBOOK rule 1).
