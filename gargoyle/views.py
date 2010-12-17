from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

from gargoyle.models import Switch, GLOBAL, DISABLED, gargoyle

def index(request):
    switches = list(Switch.objects.all().order_by("date_created"))

    return render_to_response("gargoyle/index.html", {
        "switches": switches,
        "all_conditions": list(gargoyle.get_all_conditions()),
    })

# JSON views

class GargoyleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

def json(func):
    "Decorator to make JSON views simpler"

    @wraps(func)
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

        return HttpResponse(simplejson.dumps(response), mimetype="application/json")
    return wrapper

@json
def add(request):
    key = request.POST.get("key")

    if not key:
        raise GargoyleException("Key cannot be empty")

    switch, created = Switch.objects.get_or_create(
        key         = key,
        label       = request.POST.get("name", ""),
        description = request.POST.get("desc", "")
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

    if status in (GLOBAL, DISABLED):
        switch.value["global"] = (status == GLOBAL)
    else:
        switch.value.pop("global", None)
    switch.save()

    return switch.to_dict()

@json
def delete(request):
    switch = Switch.objects.get(key=request.POST.get("key"))
    switch.delete()
    return {}
    