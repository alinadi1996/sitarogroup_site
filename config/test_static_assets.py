import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from django.conf import settings
from django.test import SimpleTestCase


class MinifiedAssetsTests(SimpleTestCase):
    def test_each_source_asset_has_a_nonempty_minified_file(self):
        static_dir = Path(settings.BASE_DIR) / 'static'
        for kind, extension in (('css', 'css'), ('js', 'js')):
            for source in (static_dir / kind).glob(f'*.{extension}'):
                output = static_dir / 'dist' / kind / f'{source.stem}.min.{extension}'
                with self.subTest(source=source.name):
                    self.assertTrue(output.is_file(), f'Missing generated asset: {output}')
                    self.assertGreater(output.stat().st_size, 0)

    def test_minified_css_font_and_icon_urls_resolve(self):
        css_dir = Path(settings.BASE_DIR) / 'static' / 'dist' / 'css'
        for stylesheet in css_dir.glob('*.css'):
            for raw_url in re.findall(r'url\(([^)]+)\)', stylesheet.read_text()):
                url = raw_url.strip().strip('\"\'')
                parsed = urlsplit(url)
                if parsed.scheme or parsed.netloc or url.startswith(('/', '#')):
                    continue
                target = stylesheet.parent / unquote(parsed.path)
                with self.subTest(stylesheet=stylesheet.name, url=url):
                    self.assertTrue(target.is_file(), f'Broken CSS asset URL: {target}')
