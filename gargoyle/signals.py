import django.dispatch

switch_added = django.dispatch.Signal(providing_args=["request", "switch"])
switch_deleted = django.dispatch.Signal(providing_args=["request", "switch"])
switch_updated = django.dispatch.Signal(providing_args=["request", "switch"])
switch_status_updated = django.dispatch.Signal(providing_args=["request", "switch", "status"])
switch_condition_added = django.dispatch.Signal(providing_args=["request", "switch", "condition"])
switch_condition_removed = django.dispatch.Signal(providing_args=["request", "switch", "condition"])
