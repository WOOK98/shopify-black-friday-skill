#!/usr/bin/env python3
"""Update dates, percentage, code and products in a LOCAL prepared theme."""
import argparse
from pathlib import Path
from prepare_campaign import read_json, write_json, validate, settings, discount_plan


def renew(theme, config):
    config = validate(config)
    theme = Path(theme)
    marker = theme / '.bfcm-local/campaign.json'
    if not marker.is_file(): raise ValueError('Expected a theme prepared by this skill')
    previous = read_json(marker)
    if config.get('suppress_footer_sections', []) != previous.get('suppress_footer_sections', []):
        raise ValueError('Changing suppressed sections requires preparing again from the baseline theme')
    data_path = theme / 'config/settings_data.json'
    data = read_json(data_path)
    data['current'].update(settings(config))
    write_json(data_path, data)
    write_json(marker, config)
    write_json(theme / '.bfcm-local/discount-plan.json', discount_plan(config))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    try: renew(args.theme, read_json(args.config))
    except (ValueError, OSError, KeyError, TypeError) as error: parser.exit(2, str(error) + '\n')
    print('Local campaign updated. Re-test and synchronize the Shopify Admin discount separately.')
