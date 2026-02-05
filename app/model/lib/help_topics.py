import re
from pathlib import Path

from flask import (
    current_app,
    render_template,
)

from markdown_it import MarkdownIt
from markupsafe import Markup
from bs4 import BeautifulSoup
from werkzeug.exceptions import NotFound


class HelpTopics:
    def __init__(self):
        self.templates_dir = Path('app/view/templates')
        self.root_dir      = self.templates_dir / 'pages/help/topics'

        self.markdown = MarkdownIt().enable('table')

        self._html_cache = {}
        self._text_cache = {}

    def render_html(self, base_path):
        try:
            return self._html_cache[base_path]
        except KeyError as e:
            raise NotFound() from e

    def search(self, query):
        results = []

        search_pattern = '(' + re.escape(query.strip()) + ')'
        regex = re.compile(search_pattern, re.IGNORECASE)

        for name, text in self._text_cache.items():
            excerpts = []
            ranges = []

            for match in re.finditer(regex, text):
                start_index = max(match.start() - 30, 0)
                end_index   = min(match.end() + 30, len(text))

                if len(ranges) > 0 and start_index in ranges[-1]:
                    # Merge with previous index:
                    ranges[-1] = range(ranges[-1].start, end_index)
                else:
                    ranges.append(range(start_index, end_index))

            excerpts = []

            for excerpt in [text[r.start:r.stop] for r in ranges]:
                # Remove possibly partial first/last word, add truncation:
                if ranges[0].start > 0:
                    excerpt = re.sub(r'^[a-zA-Z.?!,:]*\s*', '', excerpt)
                if ranges[-1].stop < len(text):
                    excerpt = re.sub(r'\s*[a-zA-Z.?!,:]*$', '', excerpt)

                excerpts.append(excerpt)

            if excerpts:
                full_excerpt = ' [...] '.join(excerpts)

                if ranges[0].start > 0:
                    full_excerpt = '...' + full_excerpt
                if ranges[-1].stop < len(text):
                    full_excerpt = full_excerpt + '...'

                results.append({
                    'name': name,
                    'excerpt_html': re.sub(regex, r'<span class="highlight">\1</span>', full_excerpt),
                })

        return results

    def process_once(self):
        if self._html_cache and not current_app.config['DEBUG']:
            return

        for file in self.root_dir.iterdir():
            extension = file.suffix
            base_path = str(file).removesuffix(extension).removeprefix(str(self.templates_dir) + '/')
            base_key  = str(file).removesuffix(extension).removeprefix(str(self.root_dir) + '/')

            if extension == '.md':
                markdown_content = render_template(f"{base_path}.md")
                html_content = Markup(self.markdown.render(markdown_content))
            elif extension == '.html':
                html_content = Markup(render_template(f"{base_path}.html"))
            else:
                html_content = None

            if html_content:
                self._html_cache[base_key] = html_content

                soup = BeautifulSoup(html_content, 'html.parser')
                self._text_cache[base_key] = ' '.join(soup.get_text(' ', strip=True).split())
