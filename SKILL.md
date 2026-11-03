---
name: shopify-black-friday-skill
description: Prepare reusable Shopify Black Friday and Cyber Monday (BFCM) campaigns, previews, private backups and restoration plans. Use for 黑五活动, 精简活动页, 订阅领码, 活动结束恢复 or annual reuse. Includes a seasonal-theme installer and guidance for minimal adaptations; does not automatically publish stores or create discounts.
---

# Shopify Black Friday Skill

Build a reviewable campaign from an existing Online Store 2.0 theme. Keep merchant data in the merchant's local project, never in this skill's repository.

## Choose the requested scope

- **Minimal campaign:** when the merchant wants a short promotion with few changes, follow [references/minimal-campaign.md](references/minimal-campaign.md). Preserve navigation, hero and product layout. This is a theme-specific adaptation workflow; the included installer does not implement this mode.
- **Seasonal homepage and coupon popup:** use the installer workflow below. It replaces the homepage during the campaign and expects a coupon code. Do not use it unchanged for an approved minimal design or an automatic-discount offer.
- **Backup or restore only:** follow [references/private-backup.md](references/private-backup.md), without introducing a new campaign design.
- **Publish the skill:** follow [docs/privacy.md](docs/privacy.md). Publish reusable authored resources and fictional examples only; keep private theme exports and recovery records outside the repository.

Keep the merchant's selected discount method. A coupon requires a code; an automatic discount must not be presented as requiring one. A reminder is a request to notify, not permission to publish.

## Workflow

1. Read the merchant's requirements and existing theme. Confirm the code, percentage, eligible merchandise, start/end timestamps with timezone, and existing welcome-offer implementation. Reuse decisions already supplied; do not ask again. Back up the current live baseline and existing welcome-offer rules using [references/private-backup.md](references/private-backup.md).
2. Check compatibility in [references/implementation.md](references/implementation.md). The included installer targets Dawn-like layouts with header/footer section groups. Stop automatic patching on unsupported layouts and adapt an isolated copy explicitly.
3. Save a private campaign JSON based on `examples/campaign.json`, outside the skill repository. Identify footer section IDs for any welcome popup that should be suppressed during the campaign. App-injected popups need their own integration; do not claim the installer disables them.
4. Run `python3 scripts/prepare_campaign.py --theme THEME_EXPORT --output SEPARATE_OUTPUT --config PRIVATE_CONFIG`. Resolve paths relative to this skill directory. Output must be new and must not be nested in the source. Preparation does not publish or call Shopify. Default `enabled` is false.
5. Customize product handles, campaign copy, hero image and translations in the output. Never fabricate reviews, shipping promises, compatibility, stock or savings. The English fallback is merged into every storefront locale; translate before multilingual launch. No product is selected by default.
6. Prepare an unpublished Shopify theme preview if authenticated access exists and the user authorizes draft upload. Otherwise present a clearly labeled local preview and state that live checkout/subscription remain unverified. For a preview during dates outside the real event, use a separate disposable preview configuration; never alter the production schedule to simulate it.
7. Follow [references/launch-and-restore.md](references/launch-and-restore.md) to check normal → active → expired behavior, mobile, signup success/error/challenge, and discount exclusivity. Run the included tests with `python3 -m unittest discover -s tests -v`; run Shopify Theme Check on the actual output. Mock tests cannot replace Shopify preview and checkout validation.
8. Present a concrete preview and outstanding checks. Respect user launch timing; publishing requires their launch instruction. A request to package, preview, or upload this skill to GitHub does not authorize publishing the merchant's storefront.
9. On launch instruction, verify the draft, backend code, dates and baseline before publishing using available authorized Shopify tooling. At expiry the theme selects the retained normal groups/homepage; the backend discount must have its own expiry. Read [references/launch-and-restore.md](references/launch-and-restore.md) before reporting restoration.
10. For next year, use `scripts/renew_campaign.py` with new explicit dates/code and `enabled: false` initially. Confirm the actual calendar, current theme changes and discount rules. Then preview and launch on instruction. Never automatically repeat a past year's schedule or overwrite the live theme with a stale annual backup.

## Output contract

Return preview/artifact paths, configuration summary, validation results, launch/restore instructions and any unverified integration. Distinguish local preparation, draft upload, backend discount setup and live publication. Do not call the workflow “one click” unless the authenticated launch and rollback integration has actually been tested.

The coupon is a public promotional code rendered in HTML, not a subscriber-only access-control mechanism. The popup reveals it visually after Shopify confirms the form; strict subscriber eligibility must be enforced in Shopify Admin. Shopify double opt-in confirmation is separate from form acceptance.

## Included resources

- `assets/theme/`: authored Liquid sections and state/clock/popup snippets, no merchant theme or product imagery.
- `assets/settings.json`, `assets/translations.json`: configurable settings and English UI copy.
- `scripts/`: local preparation and annual renewal; Python 3.10+ standard library.
- `examples/campaign.json`: fictional disabled example, not a real offer.
- `marketing/xiaohongshu/`: generated promotional materials; not published posts.
