# Private baseline and welcome-offer recovery

Use for a backup request, before preparing a campaign, and again before launch if the live theme has changed. This is a workflow for available authorized Shopify tools, not a bundled export or deployment command.

## Capture

1. Identify the current published theme and record its identifier, role, update time and shop timezone privately. Export all theme files, following every pagination cursor. Do not assume an older local theme is the current live baseline.
2. Save an immutable copy outside the public skill repository. Record relative filename, byte count and SHA-256 per file. Compare with source checksums when available. Verify the ZIP can be read and contains the expected files; do not call a partial export complete. If API text serialization differs from stored bytes, reconcile the representation or report the mismatch explicitly.
3. Read the published theme identity again. If it changed during export, reconcile or repeat the capture before calling it a consistent baseline.
4. Capture the existing welcome offer: discount identifier, code, type, status, percentage, eligible merchandise/customers, start/end dates, limits, once-per-customer setting and combination rules. Retain its popup section/snippet and enabled settings. Do not infer first-order eligibility from marketing copy.
5. Identify other active app or automatic discounts to avoid confusing them with the campaign. Record any app settings or external behavior that the theme export does not capture. A theme ZIP does not back up an entire Shopify store.

The private bundle should contain a theme ZIP, file manifest, verification result, discount snapshot and short recovery instructions. Restrict local access where available. Never upload this bundle as a public GitHub release or include it in the skill installer.

## Preserve and restore

Keep the original welcome discount and usage history intact if the intended rules allow it to remain active. Hide only its entry point during the campaign; retain the original rendering branch for expiry. Do not delete and recreate the discount to simulate restoration.

Prepare the campaign discount separately with matching timing and verify non-stacking at checkout. If the original discount must actually be suspended, restoration also requires an authorized backend reactivation path; hiding or showing theme UI cannot do that.

Retain the original theme as an emergency rollback option. At expiry remove campaign UI, stop the identified campaign discount and verify that the original welcome entry point and redemption rules work. Prefer the preserved normal branch when that avoids overwriting unrelated theme changes made during the campaign.

Report separately: backup verified, draft prepared, expiry behavior implemented, backend expiry configured and live recovery verified. A successful backup alone establishes none of the later states.
