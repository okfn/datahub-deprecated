import json

MIME_TYPES = {
        'text/html': 'html',
        'application/xhtml+xml': 'html',
        'application/json': 'json',
        'text/javascript': 'json',
        }

def request_format(request):
    """ 
    Determine the format of the request content. This is slightly 
    ugly as Flask has excellent request handling built in and we 
    begin to work around it.
    """
    return MIME_TYPES.get(request.content_type, 'html')

def request_content(request):
    """
    Handle a request and return a generator which yields all rows 
    in the incoming set.
    """
    format = request_format(request)
    if format == 'json':
        return json.loads(request.data)
    else:
        # TODO: get some kind of nested structure unrolling in here.
        return request.form.copy()

