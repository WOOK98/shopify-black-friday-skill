# Validation record

## Version 1.0.1 — 2026-11-03

Documentation and packaging update: added minimal-campaign routing, private baseline verification, welcome-offer preservation and public-release privacy review. The seasonal-homepage installer and Liquid assets are unchanged; the minimal variant is guidance for theme-specific adaptation, not a new automatic installer.

- Skill frontmatter and naming validator: passed.
- Existing Python integration suite: 14 tests passed.
- Existing Liquid/browser-clock lifecycle suite: 18 checks passed.
- Public working files, reachable Git history and the previous release ZIP: checked for known merchant/product identifiers, real offer codes, contact details, credentials and machine paths; no matches found.
- Four public promotional images: visually reviewed; no merchant screenshots or identifying product assets. PNG files contain no text or EXIF metadata chunks.

No merchant theme export or backup is part of this release. These checks do not verify a live store deployment or checkout.

## Version 1.0.0

Version 1.0.0, local checks performed on 2026-10-09.

- Skill frontmatter and naming validator: passed.
- Python integration tests: 14 tests, including immutable source/baseline, selected popup suppression, locale preservation, invalid inputs, existing/nested outputs, symlinks, contextual group rejection and annual renewal.
- Liquid/browser-clock lifecycle suite: 18 assertions covering exact time boundaries, disabled and invalid state, next year, real generated layout routing, retained non-homepage content and refresh-loop protection.
- Shopify Theme Check on the generated synthetic fixture: all 10 selected integration files passed. Standalone campaign homepage and popup validation also passed.
- Public-source privacy check: staged text reviewed for merchant identifiers, real codes, local account paths, private email addresses and credential patterns. Image visuals and metadata reviewed separately.

Fixtures contain no real merchant data. The JavaScript lifecycle suite uses LiquidJS and a mocked browser clock. These checks do not establish successful Shopify subscription, live checkout discount enforcement, third-party app behavior or CDN boundary timing. Those checks must be completed on the intended unpublished Shopify theme before a merchant launch.

Reproduce the implementation tests with `npm ci --ignore-scripts && npm test`. Theme Check should be run with current Shopify tooling against the actual adapted theme.
