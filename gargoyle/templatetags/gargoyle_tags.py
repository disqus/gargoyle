"""
gargoyle.templatetags.gargoyle_tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from django import template

from gargoyle import gargoyle

register = template.Library()

@register.tag
def ifswitch(parser, token):
    try:
        tag, name = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires an argument" % token.contents.split()[0])

    nodelist_true = parser.parse(('else', 'endifswitch'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifswitch',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    
    return SwitchNode(nodelist_true, nodelist_false, name)

class SwitchNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, name):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.name = name

    def render(self, context):
        if 'request' in context:
            conditions = [context['request']]
        else:
            conditions = []

        if not gargoyle.is_active(self.name, *conditions):
            return self.nodelist_false.render(context)

        return self.nodelist_true.render(context)