from functools import wraps

from django.conf import settings
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils import simplejson

from gargoyle import conf
from gargoyle.models import Switch, gargoyle
from gargoyle.switches import ValidationError

def login_required(func):
    def wrapped(request, *args, **kwargs):
        if not conf.PUBLIC:
            if not request.user.is_authenticated():
                return HttpResponseRedirect(reverse('gargoyle-login'))
            if not request.user.has_perm('gargoyle_switch.can_view'):
                return HttpResponseRedirect(reverse('gargoyle-login'))
        return func(request, *args, **kwargs)
    wrapped.__doc__ = func.__doc__
    wrapped.__name__ = func.__name__
    return wrapped

@login_required
def index(request):
    switches = list(Switch.objects.all().order_by("date_created"))

    return render_to_response("gargoyle/index.html", {
        "switches": [s.to_dict() for s in switches],
        "all_conditions": list(gargoyle.get_all_conditions()),
        "request": request,
    })

@csrf_protect
def login(request):
    from django.contrib.auth import login as login_
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.POST:
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login_(request, form.get_user())
            return HttpResponseRedirect(request.POST.get('next') or reverse('gargoyle'))
        else:
            request.session.set_test_cookie()
    else:
        form = AuthenticationForm(request)
        request.session.set_test_cookie()

    
    context = {
        "form": form,
        "request": request,
    }
    context.update(csrf(request))
    return render_to_response('gargoyle/login.html', context)

def logout(request):
    from django.contrib.auth import logout
    
    logout(request)
    
    return HttpResponseRedirect(reverse('gargoyle'))

# JSON views

class GargoyleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def json(func):
    "Decorator to make JSON views simpler"

    @wraps(func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            response = {
                "success": True,
                "data": func(request, *args, **kwargs)
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
    return wrapper

@json
def add(request):
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

@json
def update(request):
    switch = Switch.objects.get(key=request.POST.get("curkey"))

    if switch.key != request.POST.get("key"):
        switch.delete()
        switch.key = request.POST.get("key")

    switch.label = request.POST.get("name")
    switch.description = request.POST.get("desc")
    switch.save()

    return switch.to_dict()

@json
def status(request):
    switch = Switch.objects.get(key=request.POST.get("key"))

    try:
        status = int(request.POST.get("status"))
    except ValueError:
        raise GargoyleException("Status must be integer")

    switch.status = status
    switch.save()

    return switch.to_dict()

@json
def delete(request):
    switch = Switch.objects.get(key=request.POST.get("key"))
    switch.delete()
    return {}

@json
def add_condition(request):
    key = request.POST.get("key")
    switch_id = request.POST.get("id")
    field_name = request.POST.get("field")
    exclude = request.POST.get("exclude")
    
    if not all([key, switch_id, field_name]):
        raise GargoyleException("Fields cannot be empty")

    field = gargoyle.get_switch_by_id(switch_id).fields[field_name]
    value = field.validate(request.POST)
    
    switch = Switch.objects.get(key=key)
    switch.add_condition(switch_id, field_name, value, exclude=exclude)

    return switch.to_dict()

@json
def remove_condition(request):
    key = request.POST.get("key")
    switch_id = request.POST.get("id")
    field_name = request.POST.get("field")

    if not all([key, switch_id, field_name]):
        raise GargoyleException("Fields cannot be empty")

    field = gargoyle.get_switch_by_id(switch_id).fields[field_name]

    value = field.validate(request.POST)

    switch = Switch.objects.get(key=key)
    switch.remove_condition(switch_id, field_name, value)

    return switch.to_dict()