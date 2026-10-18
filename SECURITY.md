# Security

Video Studio runs local scripts and installs tools from their official sources. It never stores API keys.

- **Report a vulnerability** privately with GitHub's *Report a vulnerability* button on the Security tab. Please
  don't open a public issue.
- **Keys:** never commit keys or tokens. Connectors (Higgsfield, Apify) and the Fal key are configured per
  person outside the repo; see [docs/SECRETS.md](docs/SECRETS.md).
- **Downloaded media** is untrusted. The skills keep inputs in `videos/<name>/` and never execute files from them.
