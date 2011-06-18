import django.dispatch

switch_condition_added = django.dispatch.Signal(providing_args=["request"])
switch_updated = django.dispatch.Signal(providing_args=["request"])
switch_status_updated = django.dispatch.Signal(providing_args=["request"])
switch_condition_removed = django.dispatch.Signal(providing_args=["request"])
switch_added = django.dispatch.Signal(providing_args=["request"])
switch_deleted = django.dispatch.Signal(providing_args=["request"])
