from datadeck.core import app

@app.route('/api/v1/resource/<user>', methods=['GET'])
def resource_index(user):
    pass
