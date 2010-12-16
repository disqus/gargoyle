"""
gargoyle.autodiscover()

gargoyle.register(ModelSwitch(Forum, 'slug'))
gargoyle.register(ModelSwitch(Forum, 'id'))

gargoyle.register(RequestSwitch())
"""

from django.db import models

class Switch(models.Model):
    key = models.CharField(max_length=32, primary_key=True)
    value = JSONField(default="{\"disable\": true}")
    label = models.CharField(max_length=32, null=True)
    description = models.TextField(null=True)
    
    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value)
    
    def save(self, *args, **kwargs):
        super(Switch, self).save(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def delete(self, *args, **kwargs):
        super(Switch, self).delete(*args, **kwargs)
        gargoyle._populate(reset=True)
    
    def to_dict(self):
        return {
            'key': self.key,
            'status': self.get_status(),
            'active': self.is_active(),
            'label': self.label,
            'description': self.description,
        }
    
    def is_active(self):
        return not self.value.get('disable')
    
    def get_status(self):
        if self.value.get('disable'):
            return 'Disabled'
        elif self.value:
            return 'Selective'
        else:
            return 'Global'
    
    def get_for_user(self, user):
        """
        Value which is isolated to the user or default.
        """
        from django.conf import settings
        
        if not self.value:
            return True
        elif self.value.get('disable'):
            return False
        elif self.value.get('anon') and not user.is_authenticated():
            return True
        elif self.value.get('admins') and user.username in settings.DISQUS_ADMIN_USERNAMES:
            return True
        elif self.value.get('users') and user.is_authenticated():
            mod = user.id % 100
            for k in self.value['users']:
                if k == user.username:
                    return True
                if mod >= k[0] and mod <= k[1]:
                    return True
        return False
    
    def get_for_forum(self, forum):
        """
        Value which is isolated to the forum or default.
        """
        if not self.value:
            return True
        elif self.value.get('disable'):
            return False
        elif self.value.get('early_adopters') and forum.IS_EARLY_ADOPTER():
            return True
        elif self.value.get('forums'):
            mod = forum.id % 100
            for k in self.value['forums']:
                if k == forum.url:
                    return True
                if mod >= k[0] and mod <= k[1]:
                    return True
        return False
    
    def get_for_ipaddress(self, addr):
        """
        Value which is isolated to the ipaddress or default.
        """
        if not self.value:
            return True
        elif self.value.get('disable'):
            return False
        elif self.value.get('ipaddress'):
            mod = sum([int(x) for x in addr.split('.')]) % 100
            for k in self.value['ipaddress']:
                if k == addr:
                    return True
                if mod >= k[0] and mod <= k[1]:
                    return True
        return False

    def get(self):
        """
        Value which has no isolation level.
        """
        if not self.value:
            return True
        elif self.value.get('disable'):
            return False
        return False

class SettingManager(ModelDict):
    def is_active(self, key, instance=None):
        for switch in Gargoyle._registry[instance.__class__]:
            for value in self.get(key):
                if switch.is_active(instance, value):
                    return True
        return False
        
gargoyle = SettingManager(Setting, key='key', value='value', instances=True)