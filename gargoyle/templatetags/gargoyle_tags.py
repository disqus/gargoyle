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
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("%r tag requires an argument" % token.contents.split()[0])

    name = bits[1]
    instances = bits[2:]

    nodelist_true = parser.parse(('else', 'endifswitch'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifswitch',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return SwitchNode(nodelist_true, nodelist_false, name, instances)


class SwitchNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false, name, instances):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.name = name
        self.instances = [template.Variable(i) for i in instances]

    def render(self, context):
        instances = [i.resolve(context) for i in self.instances]
        if 'request' in context:
            instances.append(context['request'])

        if not gargoyle.is_active(self.name, *instances):
            return self.nodelist_false.render(context)

        return self.nodelist_true.render(context)
