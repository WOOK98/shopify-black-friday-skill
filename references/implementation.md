# Implementation

The installer reads a private theme export, checks its shape, then creates a new sibling output. It refuses an existing output, nested paths, symlinks, reserved name collisions, malformed JSON and incompatible layout structures. Contextual market-specific section groups and full footer groups require a manual adapter and are rejected. Shopify JSON exports with an initial generated comment are accepted. Existing source files are never rewritten.

## Theme changes

- Original `templates/index.json`, `sections/header-group.json` and `sections/footer-group.json` are retained byte-for-byte.
- `layout/theme.liquid` captures `bfcm-state`. It chooses duplicate campaign groups only when enabled and within the configured window. It renders `bfcm-home` only for the index route; other pages retain `content_for_layout`.
- The campaign header suppresses sections of type `announcement-bar`. The campaign footer disables its native newsletter where that setting exists, suppresses explicitly named section IDs, then adds the BFCM popup.
- Original popup code stays intact. Popups in app embeds, layout snippets or other groups need an explicit adapter before launch.
- Local settings/schema and locale namespaces are extended. The output's `.bfcm-local/` directory holds private configuration, source file hashes and a backend discount review plan. Never commit or upload this directory as part of a public skill.
- Three product pickers and an optional hero image picker provide merchant-owned content. The fallback hero is typography. Select only products eligible for the advertised discount.

## Dates

The end timestamp denotes the **last active second**. Backend `endsAt` is one second later. Example: November 30 at 23:59:59 with offset -05:00 becomes December 1 at 05:00:00 UTC for backend expiry. The installer accepts campaigns up to 93 days, with explicit matching offsets; split events spanning a daylight-saving offset change.

Both Liquid and the browser use the explicit window. Invalid or disabled state falls back to normal; the installer rejects invalid dates before output. The browser refreshes a stale tab at boundaries and on visibility/pageshow, with a short repeat-refresh guard. A suspended or offline browser cannot refresh until execution/network resumes. Verify actual caching behavior in Shopify preview.

## Newsletter and discount model

The native Shopify `customer` form is used. JavaScript reveals the code only after a confirmed success marker or a prior confirmed session. Server error text is displayed; a challenge/unknown response falls back to native submission. Clipboard failures offer manual selection. Focus returns to the opener on dialog close, and Escape uses the native dialog behavior.

The promotional code is present in page markup and is shareable. Form acceptance is not proof of completed double opt-in. Subscriber-only pricing requires Shopify backend eligibility. The preset copy advertises a percentage discount across merchandise with no other discounts; configure Shopify accordingly or adapt both code and copy. Price previews exclude taxes/shipping and rely on storefront money formatting. Verify Markets, exclusions, gift cards and rounding at checkout.

## References

Verify current official documentation when adapting or launching:

- [Shopify theme architecture](https://shopify.dev/docs/storefronts/themes/architecture)
- [Section groups](https://shopify.dev/docs/storefronts/themes/architecture/section-groups)
- [Liquid form tag](https://shopify.dev/docs/api/liquid/tags/form)
- [Discount combinations](https://help.shopify.com/en/manual/discounts/discount-combinations)
