from functools import wraps
from gargoyle import gargoyle

from django.http import Http404

def switch_is_active(key):
    def _switch_is_active(func):
        @wraps(func)
        def wrapped(request, *args, **kwargs):
            if not gargoyle.is_active(key, request):
                raise Http404('Switch \'%s\' is not active' % key)
            return func(request, *args, **kwargs)
        return wrapped
    return _switch_is_active