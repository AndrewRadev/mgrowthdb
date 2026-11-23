import json

from flask import request, g

from app.model.orm import MediumIngredient


def medium_ingredient_completion_json():
    term     = request.args.get('term', '')
    page     = int(request.args.get('page', '1'))
    per_page = 10

    results, has_more = MediumIngredient.search_by_name(g.db_session, term, page, per_page)

    return json.dumps({
        'results': results,
        'pagination': {'more': has_more},
    })
