# Validation record

Version 1.0.0, local checks performed on 2026-10-09.

- Skill frontmatter and naming validator: passed.
- Python integration tests: 14 tests, including immutable source/baseline, selected popup suppression, locale preservation, invalid inputs, existing/nested outputs, symlinks, contextual group rejection and annual renewal.
- Liquid/browser-clock lifecycle suite: 18 assertions covering exact time boundaries, disabled and invalid state, next year, real generated layout routing, retained non-homepage content and refresh-loop protection.
- Shopify Theme Check on the generated synthetic fixture: all 10 selected integration files passed. Standalone campaign homepage and popup validation also passed.
- Public-source privacy check: staged text reviewed for merchant identifiers, real codes, local account paths, private email addresses and credential patterns. Image visuals and metadata reviewed separately.

Fixtures contain no real merchant data. The JavaScript lifecycle suite uses LiquidJS and a mocked browser clock. These checks do not establish successful Shopify subscription, live checkout discount enforcement, third-party app behavior or CDN boundary timing. Those checks must be completed on the intended unpublished Shopify theme before a merchant launch.

Reproduce the implementation tests with `npm ci --ignore-scripts && npm test`. Theme Check should be run with current Shopify tooling against the actual adapted theme.
