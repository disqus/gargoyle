import nexus
import os.path

from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson

from gargoyle import gargoyle, autodiscover
from gargoyle.models import Switch, DISABLED
from gargoyle.conditions import ValidationError

GARGOYLE_ROOT = os.path.dirname(__file__)

autodiscover()

class GargoyleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def json(func):
    "Decorator to make JSON views simpler"

    def wrapper(self, request, *args, **kwargs):
        try:
            response = {
                "success": True,
                "data": func(self, request, *args, **kwargs)
            }
        except GargoyleException, exc:
            response = {
                "success": False,
                "data": exc.message
            }
        except Switch.DoesNotExist:
            response = {
                "success": False,
                "data": "Switch cannot be found"
            }
        except ValidationError, e:
            response = {
                "success": False,
                "data": u','.join(map(unicode, e.messages)),
            }
        except Exception:
            if settings.DEBUG:
                import traceback
                traceback.print_exc()
            raise
        return HttpResponse(simplejson.dumps(response), mimetype="application/json")
    wrapper = wraps(func)(wrapper)
    return wrapper

class GargoyleModule(nexus.NexusModule):
    home_url = 'index'
    name = 'gargoyle'
    
    def get_title(self):
        return 'Gargoyle'
    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': os.path.join(GARGOYLE_ROOT, 'media'),
                'show_indexes': True,
            }, name='media'),

            url(r'^add/$', self.as_view(self.add), name='add'),
            url(r'^update/$', self.as_view(self.update), name='update'),
            url(r'^delete/$', self.as_view(self.delete), name='delete'),
            url(r'^status/$', self.as_view(self.status), name='status'),
            url(r'^conditions/add/$', self.as_view(self.add_condition), name='add-condition'),
            url(r'^conditions/remove/$', self.as_view(self.remove_condition), name='remove-condition'),
            url(r'^$', self.as_view(self.index), name='index'),
        )
        
        return urlpatterns
    
    def render_on_dashboard(self, request):
        active_switches_count = Switch.objects.exclude(status=DISABLED).count()

        switches = list(Switch.objects.exclude(status=DISABLED).order_by("date_created")[:5])

        return self.render_to_string('gargoyle/nexus/dashboard.html', {
            'switches': switches,
            'active_switches_count': active_switches_count,
        })
    
    def index(self, request):
        switches = list(Switch.objects.all().order_by("date_created"))

        return self.render_to_response("gargoyle/index.html", {
            "switches": [s.to_dict() for s in switches],
            "all_conditions": list(gargoyle.get_all_conditions()),
        }, request)
    
    def add(self, request):
        key = request.POST.get("key")

        if not key:
            raise GargoyleException("Key cannot be empty")

        switch, created = Switch.objects.get_or_create(
            key         = key,
            defaults    = dict(
                label       = request.POST.get("name", ""),
                description = request.POST.get("desc", "")
            )
        )

        if not created:
            raise GargoyleException("Switch with key %s already exists" % key)

        return switch.to_dict()
    add = json(add)
    
    def update(self, request):
        switch = Switch.objects.get(key=request.POST.get("curkey"))

        if switch.key != request.POST.get("key"):
            switch.delete()
            switch.key = request.POST.get("key")

        switch.label = request.POST.get("name")
        switch.description = request.POST.get("desc")
        switch.save()

        return switch.to_dict()
    update = json(update)
    
    def status(self, request):
        switch = Switch.objects.get(key=request.POST.get("key"))

        try:
            status = int(request.POST.get("status"))
        except ValueError:
            raise GargoyleException("Status must be integer")

        switch.status = status
        switch.save()

        return switch.to_dict()
    status = json(status)
    
    def delete(self, request):
        switch = Switch.objects.get(key=request.POST.get("key"))
        switch.delete()
        return {}
    delete = json(delete)

    def add_condition(self, request):
        key = request.POST.get("key")
        condition_set_id = request.POST.get("id")
        field_name = request.POST.get("field")
        exclude = int(request.POST.get("exclude") or 0)

        if not all([key, condition_set_id, field_name]):
            raise GargoyleException("Fields cannot be empty")

        field = gargoyle.get_condition_set_by_id(condition_set_id).fields[field_name]
        value = field.validate(request.POST)

        switch = Switch.objects.get(key=key)
        switch.add_condition(condition_set_id, field_name, value, exclude=exclude)

        return switch.to_dict()
    add_condition = json(add_condition)
    
    def remove_condition(self, request):
        key = request.POST.get("key")
        condition_set_id = request.POST.get("id")
        field_name = request.POST.get("field")
        value = request.POST.get("value")

        if not all([key, condition_set_id, field_name, value]):
            raise GargoyleException("Fields cannot be empty")

        switch = Switch.objects.get(key=key)
        switch.remove_condition(condition_set_id, field_name, value)

        return switch.to_dict()
    remove_condition = json(remove_condition)

nexus.site.register(GargoyleModule, 'gargoyle')