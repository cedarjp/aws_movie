from django import forms
from django.contrib.auth.forms import UserCreationForm as _UserCreationForm
from django.contrib.auth.forms import UserChangeForm as _UserChangeForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField as _ReadOnlyPasswordHashField
from django.contrib.auth.forms import ReadOnlyPasswordHashWidget as _ReadOnlyPasswordHashWidget
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy
from bootstrap_datepicker_plus import DateTimePickerInput
from app.models import Location, State, Reason


class ReadOnlyPasswordHashWidget(_ReadOnlyPasswordHashWidget):
    template_name = 'control/user/widgets/read_only_password_hash.html'


class ReadOnlyPasswordHashField(_ReadOnlyPasswordHashField):
    widget = ReadOnlyPasswordHashWidget


class UserCreationForm(_UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", 'email', 'last_name', 'first_name', 'is_staff', )
        field_classes = {'username': UsernameField}


class SelfUserChangeForm(_UserChangeForm):
    password = ReadOnlyPasswordHashField(
        widget=forms.HiddenInput(),
        label=ugettext_lazy("Password"),
        help_text=ugettext_lazy(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ('last_name', 'first_name', 'email', 'password')
        field_classes = {'username': UsernameField}
        widgets = {
            'password': forms.HiddenInput(),
        }


class DeleteUser(forms.Form):
    username = forms.CharField(max_length=200, required=True, widget=forms.HiddenInput)

    def save(self):
        from django.contrib.auth import get_user_model
        username = self.cleaned_data['username']
        user = get_user_model().objects.get(username=username)
        user.is_active = False
        user.save()


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ('name', )


class DeleteLocation(forms.Form):
    location_id = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def save(self):
        location_id = self.cleaned_data['location_id']
        location = Location.objects.get(pk=location_id)
        location.is_active = False
        location.save()


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ('state_type', 'update_time', )
        widgets = {
            'update_time': DateTimePickerInput(
                format='%Y-%m-%d %H:%M:%S',
                options={
                    'locale': 'ja',
                    'dayViewHeaderFormat': 'YYYY年 MMMM',
                }
            ),
        }


class UploadFileForm(forms.Form):
    file = forms.FileField(label='動画ファイル')
    location = forms.ChoiceField(label='ロケーション')


class UpdateStateForm(forms.Form):
    CHOICES = ((1, '正常'), (2, '異常'), )
    location_id = forms.IntegerField()
    state_id = forms.IntegerField()
    index = forms.IntegerField()
    start_hour = forms.IntegerField()
    start_minutes = forms.IntegerField()
    start_sec = forms.IntegerField()
    end_hour = forms.IntegerField()
    end_minutes = forms.IntegerField()
    end_sec = forms.IntegerField()
    state_type = forms.ChoiceField(choices=CHOICES)
    reason = forms.ChoiceField()


class ReasonForm(forms.ModelForm):
    class Meta:
        model = Reason
        fields = ('location', 'reason', )
        widgets = {
            'location': forms.HiddenInput(),
        }


class DeleteReasonForm(forms.Form):
    reason_id = forms.IntegerField(required=True, widget=forms.HiddenInput)

    def save(self):
        reason_id = self.cleaned_data['reason_id']
        reason = Reason.objects.get(pk=reason_id)
        reason.delete()
