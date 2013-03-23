from django.core.management.base import BaseCommand, CommandError

from gargoyle.models import Switch


class Command(BaseCommand):
    args = 'switch_name'
    help = 'Removes the specified gargoyle switch.'

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError("Specify a gargoyle switch name to remove.")

        Switch.objects.filter(key=args[0]).delete()
