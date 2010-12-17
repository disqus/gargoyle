from django.conf import settings

# Allow access to Gargoyle without authentication.
PUBLIC = getattr(settings, 'GARGOYLE_PUBLIC', False)