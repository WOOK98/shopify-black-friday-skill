#!/usr/bin/env python3
"""Prepare an isolated Shopify campaign theme. Never calls Shopify or edits input."""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_DIRS = ('assets', 'blocks', 'config', 'layout', 'locales', 'sections', 'snippets', 'templates')


def read_json(path):
    # Shopify exports may begin with an auto-generated block comment.
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'^\s*/\*.*?\*/', '', text, count=1, flags=re.S)
    return json.loads(text)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def validate(config):
    allowed = {'code', 'percent', 'start_at', 'end_at', 'enabled', 'products', 'suppress_footer_sections'}
    if set(config) - allowed:
        raise ValueError('Unknown configuration keys: ' + ', '.join(sorted(set(config) - allowed)))
    for key in ('start_at', 'end_at'):
        value = config.get(key, '')
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}', value):
            raise ValueError(key + ' must be ISO 8601 with an explicit UTC offset and whole seconds')
        datetime.fromisoformat(value)
    start, end = (datetime.fromisoformat(config[k]) for k in ('start_at', 'end_at'))
    if end <= start or end - start > timedelta(days=93):
        raise ValueError('Campaign must last more than zero and no more than 93 days')
    if config['start_at'][-6:] != config['end_at'][-6:]:
        raise ValueError('Use the same fixed UTC offset for this campaign; split events spanning DST')
    if not isinstance(config.get('code'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{3,40}', config['code']):
        raise ValueError('Code must contain 3–40 letters, digits, hyphens or underscores')
    if type(config.get('percent')) is not int or not 1 <= config['percent'] <= 90:
        raise ValueError('Percent must be an integer from 1 to 90')
    if type(config.get('enabled', False)) is not bool:
        raise ValueError('Enabled must be a boolean')
    products = config.get('products', [])
    if not isinstance(products, list) or len(products) > 3:
        raise ValueError('Supply at most three product handles')
    if any(not isinstance(p, str) or not re.fullmatch(r'[a-z0-9-]+', p) for p in products):
        raise ValueError('Products must be Shopify handles')
    ids = config.get('suppress_footer_sections', [])
    if not isinstance(ids, list) or any(not isinstance(i, str) for i in ids):
        raise ValueError('suppress_footer_sections must be a list of section IDs')
    return config


def settings(config):
    result = {'bfcm_enabled': config.get('enabled', False)}
    result.update({'bfcm_' + k: config[k] for k in ('code', 'percent', 'start_at', 'end_at')})
    for i, slot in enumerate(('one', 'two', 'three')):
        result['bfcm_product_' + slot] = (config.get('products', []) + ['', '', ''])[i]
    return result


def discount_plan(config):
    return {
        'status': 'DRAFT_REQUIRES_SHOPIFY_ADMIN_SETUP',
        'code': config['code'], 'percentage': config['percent'] / 100,
        'startsAt': datetime.fromisoformat(config['start_at']).astimezone(timezone.utc).isoformat(),
        'endsAt': (datetime.fromisoformat(config['end_at']) + timedelta(seconds=1)).astimezone(timezone.utc).isoformat(),
        'combinesWith': {'orderDiscounts': False, 'productDiscounts': False, 'shippingDiscounts': False},
        'scope': 'All merchandise; verify exclusions, customer eligibility and markets before launch',
        'note': 'This is a review checklist, not an API mutation. Theme settings cannot enforce checkout rules.'
    }


def prepare(source, output, config):
    config = validate(config)
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Output and source must be separate, non-nested directories')
    if output.exists():
        raise ValueError('Output already exists; choose a new directory')
    for folder in THEME_DIRS:
        if (source / folder).is_symlink() or any(p.is_symlink() for p in (source / folder).rglob('*')):
            raise ValueError('Symlinks are not supported in theme exports')
    layout = (source / 'layout/theme.liquid').read_text(encoding='utf-8')
    if 'bfcm-state' in layout:
        raise ValueError('Theme already prepared; renew its local configuration instead')
    tokens = {
        'header': r'{%-?\s*sections\s+[\'"]header-group[\'"]\s*-?%}',
        'footer': r'{%-?\s*sections\s+[\'"]footer-group[\'"]\s*-?%}',
        'body': r'{{-?\s*content_for_layout\s*-?}}',
    }
    if any(len(re.findall(pattern, layout)) != 1 for pattern in tokens.values()) or layout.count('</body>') != 1:
        raise ValueError('Unsupported layout: expected one header-group, footer-group, content_for_layout and closing body')
    schema = read_json(source / 'config/settings_schema.json')
    data = read_json(source / 'config/settings_data.json')
    if not isinstance(data.get('current'), dict):
        raise ValueError('Theme current settings must be an object, not a named preset')
    if any(s.get('id', '').startswith('bfcm_') for g in schema for s in g.get('settings', [])):
        raise ValueError('bfcm_ settings already exist')
    if list((source / 'sections').glob('*-group.context.*.json')):
        raise ValueError('Contextual section groups require a market-specific adapter')
    header = read_json(source / 'sections/header-group.json')
    footer = read_json(source / 'sections/footer-group.json')
    if len(footer['sections']) >= 25:
        raise ValueError('Footer group has no room for another section')
    for section_id in config.get('suppress_footer_sections', []):
        if section_id not in footer['sections']:
            raise ValueError('Unknown footer section ID: ' + section_id)
    for section in header['sections'].values():
        if section.get('type') == 'announcement-bar':
            section['disabled'] = True
    for section_id, section in footer['sections'].items():
        if section_id in config.get('suppress_footer_sections', []):
            section['disabled'] = True
        if section.get('type') == 'footer' and 'newsletter_enable' in section.get('settings', {}):
            section['settings']['newsletter_enable'] = False
    if 'bfcm-popup' in footer['sections']:
        raise ValueError('Reserved section ID bfcm-popup already exists')
    footer['sections']['bfcm-popup'] = {'type': 'bfcm-popup', 'settings': {}}
    footer['order'].append('bfcm-popup')
    locales = sorted((source / 'locales').glob('*.json'))
    locales = [p for p in locales if not p.name.endswith('.schema.json')]
    if not locales:
        raise ValueError('Theme must include a storefront locale JSON file')
    translations = read_json(ROOT / 'assets/translations.json')
    merged_locales = {}
    for path in locales:
        value = read_json(path)
        if 'bfcm' in value:
            raise ValueError('bfcm locale namespace already exists')
        merged_locales[path.name] = {**value, **translations}
    for path in (ROOT / 'assets/theme').rglob('*'):
        if path.is_file() and (source / path.relative_to(ROOT / 'assets/theme')).exists():
            raise ValueError('Reserved campaign asset already exists')
    for name in ('header-group-bfcm.json', 'footer-group-bfcm.json'):
        if (source / 'sections' / name).exists():
            raise ValueError('Reserved section group already exists')
    capture = "{% capture bfcm_state %}{% render 'bfcm-state' %}{% endcapture %}\n{% assign bfcm_state = bfcm_state | strip %}\n"
    layout = capture + layout
    for name in ('header', 'footer'):
        layout = re.sub(tokens[name], lambda m: "{% if bfcm_state == 'active' %}{% sections '" + name + "-group-bfcm' %}{% else %}" + m[0] + '{% endif %}', layout)
    layout = re.sub(tokens['body'], lambda m: "{% if bfcm_state == 'active' and request.page_type == 'index' %}{% section 'bfcm-home' %}{% else %}" + m[0] + '{% endif %}', layout)
    layout = layout.replace('</body>', "{% render 'bfcm-clock', state: bfcm_state %}\n</body>")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.bfcm-', dir=output.parent))
    try:
        baseline = {}
        for folder in THEME_DIRS:
            if (source / folder).is_dir():
                shutil.copytree(source / folder, temporary / folder)
                for p in (source / folder).rglob('*'):
                    if p.is_file(): baseline[str(p.relative_to(source))] = hashlib.sha256(p.read_bytes()).hexdigest()
        shutil.copytree(ROOT / 'assets/theme', temporary, dirs_exist_ok=True)
        (temporary / 'layout/theme.liquid').write_text(layout, encoding='utf-8')
        write_json(temporary / 'sections/header-group-bfcm.json', header)
        write_json(temporary / 'sections/footer-group-bfcm.json', footer)
        schema.append(read_json(ROOT / 'assets/settings.json'))
        data['current'].update(settings(config))
        write_json(temporary / 'config/settings_schema.json', schema)
        write_json(temporary / 'config/settings_data.json', data)
        for name, value in merged_locales.items(): write_json(temporary / 'locales' / name, value)
        write_json(temporary / '.bfcm-local/campaign.json', config)
        write_json(temporary / '.bfcm-local/discount-plan.json', discount_plan(config))
        write_json(temporary / '.bfcm-local/baseline-hashes.json', baseline)
        temporary.rename(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare(args.theme, args.output, read_json(args.config))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, 'Preparation failed: ' + str(error) + '\n')
    print('Prepared local theme. Campaign enabled only if configured. Nothing uploaded or published.')


if __name__ == '__main__':
    main()
