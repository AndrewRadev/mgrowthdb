from flask import (
    request,
    render_template,
)

from app.model.lib.util import is_ajax
from app.model.lib.help_topics import HelpTopics


HELP_TOPICS = HelpTopics()


def help_index_page():
    HELP_TOPICS.process_once()

    if len(request.args.get('query', '')) >= 3:
        topics = HELP_TOPICS.search(request.args['query'])
    else:
        topics = None

    if is_ajax(request):
        return render_template("pages/help/_topic_list.html", topics=topics)
    else:
        return render_template("pages/help/index.html", topics=topics)


def help_show_page(name):
    HELP_TOPICS.process_once()

    title = name.replace('-', ' ').title()
    html_content = HELP_TOPICS.render_html(name)

    return render_template("pages/help/show.html", title=title, content=html_content)
