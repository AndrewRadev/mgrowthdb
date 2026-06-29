import re

from markupsafe import Markup
from flask import url_for

from app.view.filters.text import highlight

_ORCID_REGEX = re.compile(r'https?://orcid.org/[0-9-]+')


def ncbi_url(ncbi_id):
    return f"https://www.ncbi.nlm.nih.gov/datasets/taxonomy/{ncbi_id}/"


def chebi_url(chebi_id):
    return f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId={chebi_id}"


def external_link(url, text=None, css_class=''):
    text = text or url

    return Markup(
        f"""<a class="external {css_class}" target="_blank" rel="noreferrer" href="{url}">{text}</a>"""
    )


def help_link(page_name, text=None, section=None, css_class=''):
    text = text or page_name.replace('-', ' ').title()
    url = url_for('help_show_page', name=page_name)

    if section:
        url += '#'
        url += section

    return Markup(f"""<a class="{css_class}" target="_blank" href="{url}">{text}</a>""")


def author_link_list(authors, query_words=None, limit=None):
    link_list = []
    remaining = 0

    # Highlight search terms if a query is given:
    if query_words:
        search_pattern = '(' + '|'.join([re.escape(w) for w in query_words]) + ')'
        query_regex = re.compile(search_pattern, re.IGNORECASE)
    else:
        query_regex = None

    for i, author in enumerate(authors):
        # Only the first `limit` authors are shown, unless they are marked as "first":
        if limit is not None and i >= limit and author["sequence"] != 'first':
            remaining = len(authors) - i
            break

        link_list.append(_render_author_name(author, query_words, query_regex))

    # If any of the hidden users also match the query, add them to the list:
    if remaining > 0 and query_words:
        for author in authors[len(link_list):]:
            if re.match(query_regex, author['family']):
                link_list.append(_render_author_name(author, query_words, query_regex))
                remaining -= 1

    if remaining > 0:
        link_list.append(f"and {remaining} more")

    return Markup(', '.join(link_list))


def _render_author_name(author, query_words, query_regex):
    # John D. Name -> Name, J. D.
    short_given_name = ' '.join([f"{n[0]}." for n in author['given'].split()])
    name = f"{author['family']}, {short_given_name}"

    if query_regex:
        name = highlight(name, query_words, query_regex)

    # If there is an ORCID URL, link the user:
    if "ORCID" in author and re.fullmatch(_ORCID_REGEX, author["ORCID"]):
        return f"""<a target="_blank" href="{author["ORCID"]}">{name}</a>"""
    else:
        return name
