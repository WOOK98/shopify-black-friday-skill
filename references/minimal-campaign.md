# Minimal campaign adaptation

Use this path when the merchant approves a small, temporary promotion. The bundled `prepare_campaign.py` creates a different, full seasonal homepage with a coupon popup; it is not a minimal-mode installer. Adapt an isolated copy of the current theme using its actual sections and price snippets.

## Scope and state

Keep the existing navigation, hero, product order and mobile layout. Add only the approved announcement, offer explanation and popup changes. Do not introduce new landing-page sections, cart demos or a redesign unless requested.

Use one explicit campaign window and an enabled flag for all campaign UI. Retain the normal rendering branch, including the welcome-offer popup and its settings. Outside the window, select that branch and remove campaign announcements, estimated prices, temporary strike-through styling and cart offer text together. Reuse the state/clock snippets only with their documented inclusive-end convention; align the backend exclusive expiry accordingly.

If requested, strike through only the current price amount during the active window and show a clearly labeled estimated checkout price beside or below it. Keep product prices and compare-at values unchanged. Calculate using the selected variant and currency; re-evaluate on variant changes. Avoid estimates for ineligible products or discounts whose allocation cannot be represented accurately. Checkout remains authoritative.

## Discount and welcome offer

Use the merchant's chosen method. For a code, explain where it is entered and when it is valid. For an automatic discount, explain that it applies at checkout and do not invent a code or mandatory signup step. Do not silently switch between these methods.

Follow [private-backup.md](private-backup.md) to preserve the welcome discount's identifier, rules and usage history. Usually only its entry point needs temporary suppression. Set the campaign discount's own expiry and intended combination rules with authorized Shopify tooling. Verify how it interacts with the original welcome discount and app promotions. Theme code cannot enforce non-stacking.

## Acceptance and handoff

- Before start and after expiry: the normal homepage, regular price presentation and original welcome entry point appear.
- Active: approved announcement, price display and offer method agree with the actual checkout rules.
- Mobile and variant changes: no overflow, stale estimates or misplaced strike-through styling.
- Checkout: eligible and ineligible merchandise, welcome-code interaction, app discounts, rounding and currency are verified.
- Recovery: a verified baseline is retained; campaign UI and backend discount have independent end handling.

Present the preview, exact dates with timezones, restore behavior and remaining live checks. Keep launch authorization separate from design approval. For annual reuse, adapt the current theme with new dates rather than reinstalling a stale merchant export.
