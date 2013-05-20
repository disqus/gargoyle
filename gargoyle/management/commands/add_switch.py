from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

from gargoyle.models import Switch, DISABLED, GLOBAL


class Command(BaseCommand):
    args = 'switch_name'
    help = 'Adds or updates the specified gargoyle switch.'

    option_list = BaseCommand.option_list + (
        make_option(
            '--disabled',
            action='store_const',
            const=DISABLED,
            default=GLOBAL,
            dest='status',
            help='Create a disabled switch.'),
    )

    def handle(self, *args, **kwargs):
        if len(args) != 1:
            raise CommandError("Specify a gargoyle switch name to add.")

        status = kwargs['status']
        switch, created = Switch.objects.get_or_create(
            key=args[0],
            defaults=dict(status=status),
        )
        if not created and switch.status != status:
            switch.status = status
            switch.save()
