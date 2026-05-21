def init_compare_data(session):
    data = session.get('compareData', {})

    if 'contexts' not in data:
        data['contexts'] = []
    if 'models' not in data:
        data['models'] = []

    return data
