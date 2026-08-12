---
status: accepted
---
# First-party Comments in D1 replace Giscus

Giscus was correctly configured and produced zero discussion threads, because it
demands a GitHub account and a third-party OAuth grant before a reader can type,
from a readership that is majority Chinese. It also stores threads in GitHub
Discussions, which makes answering readers from the Admin structurally
impossible. Comments therefore become first-party rows in D1.

## Consequences

- Commenters are anonymous by design — a display name and nothing else. Every
  login option available was either blocked (Google), unreliable from the
  mainland (GitHub) or high-friction (email link), and the evidence that friction
  produces silence is already in hand.
- ~~Bot resistance comes from Cloudflare Turnstile, chosen over reCAPTCHA
  because it is reachable from mainland China.~~ **VOID — the premise is false.**
  Cloudflare documents: "Turnstile is not supported in Mainland China."
  (https://developers.cloudflare.com/china-network/faq/, verified 2026-08-11).
  Turnstile was selected *solely* on mainland reachability, so the rationale does
  not survive; the decision is reopened.
- **Replacement, decided 2026-08-11:** rate limiting plus a honeypot field as the
  always-on first-party baseline, escalating to a self-hosted ALTCHA
  proof-of-work challenge for untrusted or suspicious clients. Both are served
  from `stometa.dev` itself, so there is no third-party host that can be blocked. hCaptcha is
  rejected as a default because its mandatory third-party endpoints carry no
  primary-source mainland availability guarantee. See
  `docs/designs/stometa-dev/verification-cloudflare.md` C4 for the comparison.
- A Commenter's first Comment waits in the Moderation Queue; approving it makes
  them a Trusted Commenter. This trades a standing chore for never having spam
  visible on the page.
- Nothing needs migrating: there are no existing comments.
