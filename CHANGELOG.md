# Changelog

All notable changes to this project are documented here. Versions follow [SemVer](https://semver.org).

## [0.1.0] - 2026-10-19
First release.

### Added
- **Studio skills:** `studio` (front door / router), `chop-reel`, `launch-film` (with the fold-cut builder),
  `ugc-ads`, `ugc-actor`, `product-demo` (cursor tracking, auto camera, VO from SRT, ducked mix), `art-styles`,
  `score` (synth library, 3 example scores, beat detection), `caption-video` (7 styles, hooks, audio polish).
- **Templates:** `hello-world` (8 s proof render) and `chop-reel` (12 s engine that renders 16:9 + 9:16).
- **Examples with full source:** The Brief, Great Pyramid, Twelve Painters, Eight Eras.
- **Setup:** `setup/setup.sh` (idempotent, per-step `--only`), `setup/doctor.sh`, pinned versions, and a
  session-start hook that checks setup when Claude Code opens the folder.
- **Docs:** PLAYBOOK (21 house rules), CATALOG (every tool, cost and source), SECRETS, architecture diagram.
- Plugin manifest so the skills can be installed in every folder.
