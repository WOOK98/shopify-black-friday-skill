# Public package privacy boundary

This repository contains reusable authored components and fictional examples only. It excludes merchant/store identifiers, real coupon codes, customer/order information, margins and sales data, product imagery, theme exports, account settings, credentials, original site backups and local machine paths.

The repository owner's public GitHub handle and GitHub noreply commit identity remain part of normal repository attribution. They are not store credentials or a personal email address.

Keep real campaign JSON, generated themes, source exports and `.bfcm-local` files outside this repository. `.gitignore` adds a defense, but is not a data-loss prevention system. Review all staged files and history before publishing changes. Screenshots can contain private content even when filenames are generic; use fictional graphics for public promotion.

The marketing images are AI-generated concept art or rendered generic cards. No customer image or actual merchant screenshot is included. This skill sends no emails, uploads no customer data and contains no telemetry.

## Release review

1. Inspect the exact tracked files and staged diff. Publish from the skill directory only, never its parent workspace. Package from a reviewed commit, for example with `git archive`, rather than recursively zipping a working directory.
2. Search content and filenames for merchant names and aliases, public and internal domains, product names/handles/SKUs, real discount codes, Shopify identifiers, contact details, credentials, local paths and commercial metrics. Keep the search terms private; do not commit a denylist containing the merchant's real identifiers.
3. Review all reachable Git history, not only the latest files. Check existing release assets when re-publishing a previously released project. A deletion in a new commit does not remove data from older commits or ZIPs.
4. Inspect promotional images visually and inspect embedded metadata. Generic filenames do not anonymize store screenshots. Use authored fictional examples instead of blurring a real store incompletely.
5. Inspect the final archive member list, run the same checks on its contents, and verify its checksum after upload. Exclude `.git`, private backups, credentials, generated merchant themes and local runtime files.

Use fictional values such as `DEMO10` and empty product selections. Preserve useful algorithms, configuration structure and recovery instructions; do not copy a merchant's actual offer, catalog or theme into a reusable example. If a historical leak is found, identify the affected commits and assets and prepare a specific cleanup; do not claim that editing the latest README removes the old data.
