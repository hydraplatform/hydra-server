"""
    Request header handling which does not depend on spyne so it can be tested in isolation.
"""

# Request headers which are copied on to ctx.in_header. 'user_id' and 'username' are
# overwritten from the session before any function is called.
ALLOWED_HEADER_FIELDS = ('username', 'user_id', 'appname', 'app_name')


def filter_header_fields(header_doc):
    """
        Return a dict of the header fields that may be set on ctx.in_header.

        The handlers pass ctx.in_header.__dict__ on to the library functions as keyword
        arguments, so only declared fields are accepted. Any other header is dropped.
    """
    return {k: v[0] for k, v in header_doc.items() if k in ALLOWED_HEADER_FIELDS}
