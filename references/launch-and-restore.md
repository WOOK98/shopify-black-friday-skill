# Launch, restore and annual reuse

## Before launch

1. Keep a private original theme export and its live theme identifier. Run local tests and Shopify Theme Check on the generated theme. Ensure header/footer/popup adapters match the actual store.
2. Upload only a draft theme using authorized Shopify tooling. Keep `.bfcm-local` outside the uploaded theme archive. Preview both desktop and mobile and check homepage, product, collection, cart and navigation.
3. Use a separate disposable preview to simulate before start, exact start, final active second, expiry, disabled state and next-year dates. Verify that original homepage, announcement/footer and welcome popup reappear.
4. Test newsletter rejection, successful submission, double opt-in/challenge if enabled, Escape/focus, code copy, apply-code link, and new versus returning visitors. Verify customer records in Shopify; mocks are not evidence of delivery or subscription.
5. Create or update the actual percentage code in Shopify Admin with matching scope/percentage, start and expiry, and all three combination flags disabled if the offer excludes stacking. Check the existing welcome offer and any discount app/automatic promotion. Run checkout tests for each combination and relevant market.
6. Confirm the prepared theme has the intended future window and code, not the disposable preview dates. Review the private `.bfcm-local/discount-plan.json` against Admin.
7. Publish only on the merchant's launch instruction. If a reminder was requested, schedule a reminder using the host scheduler; a reminder must not silently become publication.

## At and after expiry

The campaign branch stops rendering outside its time window, so the retained original homepage, groups and their original settings are selected again. Open tabs request a refresh when they reach the boundary or wake. The backend discount must expire independently in Shopify Admin.

After expiry verify the live homepage, welcome popup and checkout. If the merchant needs immediate manual rollback, publish the saved original theme or disable `bfcm_enabled` on the campaign theme, then verify. Disabling the theme setting does **not** deactivate a backend discount; deactivate it in Admin separately if needed. Never revert unrelated product/order/customer changes.

## Next year

Reuse the skill and settings, not an obsolete full-store snapshot. Export/reconcile the current live theme; use the installer on that fresh export where possible. If renewing an already prepared local theme, review all changes made since the prior campaign and use `renew_campaign.py` with explicit new dates, code and selected products. Start with `enabled: false`, then repeat preview and checkout validation before the authorized launch.

For illustration, 2027 Black Friday is November 26 and Cyber Monday is November 29; do not blindly reuse the prior year's November 30 deadline. Shipping cutoffs, product availability, welcome offers and business rules may change.

## Completion report

Report separately: local files prepared, theme draft uploaded, backend discount configured, storefront published, expiry verified. Mark unperformed live checks as pending. This package itself provides local preparation and conditional restoration; it does not provide an authenticated universal one-click Shopify deploy button.
