# Cost policy

**Policy:** Do not incur costs, start paid trials, enter payment details, purchase domains, or enable billable services without explicit owner approval.

## Current Phase 1 inventory

| Component | Current use | Cost status | Notes / risk |
|---|---|---|---|
| HTML, CSS, JavaScript | Browser interface | No service charge | Runs locally in a browser. |
| Browser `localStorage` | Glossary and preferences | No service charge | Limited by browser quota; user can clear data. |
| External fonts stylesheet | Optional typography request in CSS | No direct charge expected, but contacts Google Fonts | Network request and third-party privacy dependency. For a strict offline/privacy build, remove the `@import` and use system fonts. |
| Translation API/model | Not configured | Disabled | No text is sent for translation; no translation result is fabricated. |
| Hosting/domain/database/payment | Not configured | Disabled | No deployment or purchases have been made. |

## Rules for future phases

1. Prefer local execution and open-source tools where technically practical.
2. Verify current pricing, quotas, card requirements, terms, privacy policy, and commercial-use rights before use.
3. Never enable a service if a payment method is required or costs could be triggered without safeguards and approval.
4. Do not assume a free tier is unlimited or permanent.
5. Keep secrets out of frontend code and repository.
6. Record each new dependency, model, service, license, cost risk, and free alternative here.
7. Stop before any purchase, subscription, paid trial, or potentially billable deployment step.

## Future options to investigate (not approved or activated)

Static hosting such as Cloudflare Pages or GitHub Pages may have free plans, but current terms and limits must be verified at the time of deployment. Local translation models may avoid per-request API fees but can require significant downloads, memory, CPU, and compatible licenses. No option is guaranteed free forever.

## Cost-safe decision rule

If the service's zero-cost status cannot be verified for the intended use, leave it disabled and document a no-cost alternative.
