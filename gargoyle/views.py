from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

from gargoyle.models import Switch

json = lambda data: HttpResponse(simplejson.dumps(data), mimetype="application/json")

def index(request):
    switches = list(Switch.objects.all().order_by("date_created"))

    return render_to_response("gargoyle/index.html", {
        "switches": switches
    })

def add(request):
    switch = Switch.objects.create(
        label       = request.POST.get("name"),
        key         = request.POST.get("key"),
        description = request.POST.get("desc")
    )

    return json(switch.to_dict())
    
def status(request):
    try:
        switch = Switch.objects.get(key=request.POST.get("key"))
    except Switch.DoesNotExist:
        return {}
    return {}


def delete(request):
    try:
        switch = Switch.objects.get(key=request.POST.get("key"))
        switch.delete()
    except Switch.DoesNotExist:
        return json({ "success": False })

    return json({ "success": True })
    