import re

from markupsafe import Markup
from flask import url_for

from app.view.filters.text import highlight


def ncbi_url(ncbi_id):
    return f"https://www.ncbi.nlm.nih.gov/datasets/taxonomy/{ncbi_id}/"


def chebi_url(chebi_id):
    return f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId={chebi_id}"


def external_link(url, text=None, css_class=''):
    text = text or url

    return Markup(f"""<a class="external {css_class}" target="_blank" rel="noreferrer" href="{url}">{text}</a>""")


def help_link(page_name, text=None, section=None, css_class=''):
    text = text or page_name.replace('-', ' ').title()
    url = url_for('help_show_page', name=page_name)

    if section:
        url += '#'
        url += section

    return Markup(f"""<a class="{css_class}" target="_blank" href="{url}">{text}</a>""")


def author_link_list(authors, format="short", query_words=None):
    link_list = []

    if query_words:
        search_pattern = '(' + '|'.join([re.escape(w) for w in query_words]) + ')'
        regex = re.compile(search_pattern, re.IGNORECASE)
    else:
        regex = None

    for author in authors:
        if format == 'long' or (regex and re.match(regex, author['given'])):
            name = f"{author['given']} {author['family']}"
        elif format == 'short':
            short_given_name = ' '.join([f"{n[0]}." for n in author['given'].split()])
            name = f"{author['family']}, {short_given_name}"
        else:
            raise ValueError(f"Unknown format: {format}")

        if regex:
            name = highlight(name, query_words, regex)

        if "ORCID" in author and re.fullmatch(r'https?://orcid.org/[0-9-]+', author["ORCID"]):
            link_list.append(f"""<a target="_blank" href="{author["ORCID"]}">{name}</a>""")
        else:
            link_list.append(name)

    return Markup(', '.join(link_list))
