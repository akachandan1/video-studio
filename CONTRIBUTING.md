# Contributing

Thanks for helping make Video Studio better. The best contributions are **techniques proven on a real video**:
a workflow, a template, a transition, a sound, or a house rule learned the hard way.

## Ways to contribute
- **Showcase:** made something with the studio? Open a *Showcase* issue with a link. The best ones go in the README gallery.
- **New workflow skill:** `.claude/skills/<name>/SKILL.md`. Copy the shape of an existing one: front-matter
  `name` + a `description` that says *when* to use it, then numbered steps, exact commands, and what to check before delivering.
- **Template:** `templates/<name>/` must render with no edits: `lint` clean and `render` succeeds in both aspects if it claims both.
- **Playbook rule:** add to `docs/PLAYBOOK.md` with a **Why** (what went wrong without it).
- **Fixes:** setup on new macOS versions, doctor checks, broken commands.

## Ground rules
1. **HyperFrames is the core.** New tools should produce assets that HyperFrames assembles, not replace it.
2. **No third-party code copied in.** Add it to `setup/setup.sh` (installed from its official source) and to
   `ACKNOWLEDGMENTS.md` + `docs/CATALOG.md`. If you adapt or port someone's code or specs, keep their
   attribution line in the file and add their license text to `THIRD_PARTY_NOTICES.md`.
3. **No client material, footage you don't own, brand assets, or keys.** Examples must be original or properly licensed.
4. **Free by default.** Paid generation must stay optional and must always quote its cost before running.
5. Keep commands copy-pasteable and paths quoted (folders often contain spaces).

## Before you open a PR
```bash
setup/doctor.sh
for t in templates/*/; do (cd "$t" && ../../.venv/bin/python score.py >/dev/null && \
  { [ -f build.py ] && ../../.venv/bin/python build.py 169 >/dev/null || true; } && \
  npx --yes hyperframes@$(grep HYPERFRAMES_VERSION ../../setup/versions.env | cut -d= -f2 | cut -d' ' -f1) lint); done
```
CI runs the same lint plus shell, Python and JSON checks on every PR.

## Commit style
Short imperative subject (`Add whip-pan block to chop-reel`), body explains *why*. One topic per PR.
