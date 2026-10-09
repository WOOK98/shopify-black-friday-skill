import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from prepare_campaign import prepare, read_json, write_json, validate, discount_plan
from renew_campaign import renew


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source, self.output = self.base / 'original', self.base / 'prepared'
        self.config = read_json(ROOT / 'examples/campaign.json')
        for folder in ('layout', 'templates', 'sections', 'config', 'locales', 'assets'):
            (self.source / folder).mkdir(parents=True)
        (self.source / 'layout/theme.liquid').write_text('<!doctype html><html><head>{{ content_for_header }}</head><body>{% sections "header-group" %}<main>{{ content_for_layout }}</main>{%- sections \'footer-group\' -%}</body></html>')
        write_json(self.source / 'sections/header-group.json', {'type': 'header', 'name': 'Header', 'sections': {'announcement': {'type': 'announcement-bar'}, 'header': {'type': 'header'}}, 'order': ['announcement', 'header']})
        write_json(self.source / 'sections/footer-group.json', {'type': 'footer', 'name': 'Footer', 'sections': {'footer': {'type': 'footer', 'settings': {'newsletter_enable': True}}, 'welcome': {'type': 'welcome-popup'}}, 'order': ['footer', 'welcome']})
        for name in ('header', 'footer', 'announcement-bar', 'welcome-popup', 'main'):
            (self.source / 'sections' / (name + '.liquid')).write_text('{% schema %}{"name":"Test","settings":[]}{% endschema %}')
        write_json(self.source / 'config/settings_schema.json', [])
        write_json(self.source / 'config/settings_data.json', {'current': {'unrelated': 'preserve'}})
        write_json(self.source / 'templates/index.json', {'sections': {'main': {'type': 'main'}}, 'order': ['main']})
        write_json(self.source / 'locales/en.default.json', {'general': {'hello': 'Hello'}})
        write_json(self.source / 'locales/fr.json', {'general': {'hello': 'Bonjour'}})
        self.config['suppress_footer_sections'] = ['welcome']

    def snapshot(self):
        return {str(p.relative_to(self.source)): p.read_bytes() for p in self.source.rglob('*') if p.is_file()}

    def test_prepare_preserves_input_and_normal_content(self):
        before = self.snapshot()
        prepare(self.source, self.output, self.config)
        self.assertEqual(before, self.snapshot())
        for name in ('templates/index.json', 'sections/header-group.json', 'sections/footer-group.json', 'sections/welcome-popup.liquid'):
            self.assertEqual((self.source / name).read_bytes(), (self.output / name).read_bytes())
        data = read_json(self.output / 'config/settings_data.json')['current']
        self.assertEqual(data['unrelated'], 'preserve')
        self.assertFalse(data['bfcm_enabled'])
        self.assertEqual(data['bfcm_product_one'], '')

    def test_active_groups_suppress_only_selected_popup(self):
        prepare(self.source, self.output, self.config)
        header = read_json(self.output / 'sections/header-group-bfcm.json')
        footer = read_json(self.output / 'sections/footer-group-bfcm.json')
        self.assertTrue(header['sections']['announcement']['disabled'])
        self.assertNotIn('disabled', header['sections']['header'])
        self.assertTrue(footer['sections']['welcome']['disabled'])
        self.assertFalse(footer['sections']['footer']['settings']['newsletter_enable'])
        self.assertIn('bfcm-popup', footer['order'])

    def test_locales_retain_original_keys(self):
        prepare(self.source, self.output, self.config)
        french = read_json(self.output / 'locales/fr.json')
        self.assertEqual(french['general']['hello'], 'Bonjour')
        self.assertIn('bfcm', french)

    def test_backend_end_is_exclusive_and_no_combinations(self):
        plan = discount_plan(self.config)
        self.assertEqual(plan['endsAt'], '2026-12-01T05:00:00+00:00')
        self.assertEqual(plan['percentage'], .1)
        self.assertFalse(any(plan['combinesWith'].values()))

    def test_renew_changes_year_without_overwriting_baseline(self):
        prepare(self.source, self.output, self.config)
        baseline = (self.output / 'templates/index.json').read_bytes()
        updated = {**self.config, 'start_at': '2027-11-15T00:00:00-05:00', 'end_at': '2027-11-29T23:59:59-05:00', 'code': 'DEMO2027', 'percent': 15}
        renew(self.output, updated)
        current = read_json(self.output / 'config/settings_data.json')['current']
        self.assertEqual(current['bfcm_code'], 'DEMO2027')
        self.assertEqual(current['bfcm_percent'], 15)
        self.assertEqual(baseline, (self.output / 'templates/index.json').read_bytes())
        self.assertEqual(read_json(self.output / '.bfcm-local/discount-plan.json')['endsAt'], '2027-11-30T05:00:00+00:00')

    def test_invalid_config_does_not_create_output(self):
        cases = [{'start_at': '2026-11-16'}, {'end_at': '2026-11-15T00:00:00-05:00'}, {'end_at': '2026-11-30T23:59:59-04:00'}, {'percent': True}, {'percent': 101}, {'code': '<script>'}, {'enabled': 'true'}, {'products': ['../private']}]
        for patch in cases:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                prepare(self.source, self.output, {**self.config, **patch})
            self.assertFalse(self.output.exists())

    def test_unsupported_layout_fails_before_writing(self):
        (self.source / 'layout/theme.liquid').write_text('{{ content_for_layout }}')
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)
        self.assertFalse(self.output.exists())

    def test_unknown_popup_is_not_silently_ignored(self):
        self.config['suppress_footer_sections'] = ['missing']
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir(); (self.output / 'keep').write_text('keep')
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)
        self.assertEqual((self.output / 'keep').read_text(), 'keep')

    def test_nested_output_and_symlinks_rejected(self):
        with self.assertRaises(ValueError): prepare(self.source, self.source / 'nested', self.config)
        (self.source / 'assets/link').symlink_to(self.source / 'templates/index.json')
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)

    def test_export_comment_supported(self):
        path = self.source / 'sections/header-group.json'
        path.write_text('/* Generated configuration. */\n' + path.read_text())
        prepare(self.source, self.output, self.config)
        self.assertTrue(self.output.exists())

    def test_contextual_groups_require_adapter(self):
        write_json(self.source / 'sections/header-group.context.demo.json', {'parent': 'header-group.json'})
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)
        self.assertFalse(self.output.exists())

    def test_full_footer_group_is_rejected(self):
        path = self.source / 'sections/footer-group.json'
        footer = read_json(path)
        for i in range(23):
            footer['sections'][str(i)] = {'type': 'footer'}
            footer['order'].append(str(i))
        write_json(path, footer)
        with self.assertRaises(ValueError): prepare(self.source, self.output, self.config)
        self.assertFalse(self.output.exists())

    def test_reinstall_and_changed_popup_renewal_rejected(self):
        prepare(self.source, self.output, self.config)
        with self.assertRaises(ValueError): prepare(self.output, self.base / 'second', self.config)
        with self.assertRaises(ValueError): renew(self.output, {**self.config, 'suppress_footer_sections': []})


if __name__ == '__main__': unittest.main()
