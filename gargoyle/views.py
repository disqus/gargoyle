from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

def render(template, user_values=None):
    values = {
        "media": reverse("gargoyle-media"),
    }
    print reverse("gargoyle-media")
    if user_values:
        values.updated(user_values)
    return render_to_response(template, values)

def index(request):
    return render("gargoyle/index.html")