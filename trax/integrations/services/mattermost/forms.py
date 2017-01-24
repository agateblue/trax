from django import forms
from django.conf import settings
from dynamic_preferences.registries import global_preferences_registry

from trax.users.models import User
from . import handlers_registry


class SlashCommandForm(forms.Form):
    token = forms.CharField()
    channel_id = forms.CharField()
    channel_name = forms.CharField()
    command = forms.CharField()
    team_domain = forms.CharField()
    team_id = forms.CharField()
    user_id = forms.CharField()
    user_name = forms.CharField()
    text = forms.CharField()

    # will be deduced from command
    handler = forms.CharField(required=False)
    action = forms.CharField(required=False)
    arguments = forms.CharField(required=False)

    # will be deduced from user id
    user = forms.ModelChoiceField(required=False, queryset=User.objects.all())
    #
    # def clean_token(self):
    #     global_preferences = global_preferences_registry.manager()
    #     expected_token = global_preferences['trax__slash_command_token']
    #     if expected_token != self.cleaned_data['token']:
    #         raise forms.ValidationError('Invalid token')
    #     return self.cleaned_data['token']

    def clean_user(self):
        # First, we try to bind to an existing user without external ID
        try:
            user = User.objects.get(
                username=self.cleaned_data['user_name'],
                external_id__isnull=True)
            user.external_id = self.cleaned_data['user_id']
            user.save()
            return user
        except User.DoesNotExist:
            pass

        # otherwise, we fallback to simply creating a user from scratch
        return User.objects.get_or_create(
            external_id=self.cleaned_data['user_id'],
            username=self.cleaned_data['user_name'],
            defaults={
                'is_active': False,
            }
        )[0]

    def clean_action(self):
        try:
            return self.cleaned_data['text'].split(' ')[0].strip()
        except KeyError:
            # No arguments were sent, we fallback on help
            return 'help'

    def clean_arguments(self):
        try:
            return ' '.join(self.cleaned_data['text'].split(' ')[1:]).strip()
        except KeyError:
            return ''

    def clean_handler(self):
        action = self.clean_action()
        try:
            return [h for h in handlers_registry.handlers if h.valid_for_action(action)][0]
        except IndexError:
            raise forms.ValidationError('No handler found for action {0}'.format(action))
