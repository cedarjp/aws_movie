import os

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView, FormView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import ContextMixin
from django.http.response import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse


from app import models
from app import forms
from app.tasks import s3_upload_task, s3_upload_obj_task
# Create your views here.


class Index(LoginRequiredMixin, ListView):
    """
    動画一覧画面
    """
    template_name = "root/index.html"
    model = models.State
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context_data = super(Index, self).get_context_data(object_list=object_list, **kwargs)
        context_data['last_object'] = self.model.objects.all().first()
        context_data['upload_file_form'] = forms.UploadFileForm()
        return context_data

    def get_queryset(self):
        queryset = super(Index, self).get_queryset()[1:]
        return queryset


class Detail(DetailView):
    model = models.State
    template_name = "root/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super(Detail, self).get_context_data(**kwargs)
        context_data['status_types'] = forms.UpdateStateForm.CHOICES
        context_data['reason_list'] = models.Reason.get_choices_list(location_id=context_data['object'].location_id)
        return context_data


class State(View):
    """
    最新の状態をjsonで返却
    """

    def get(self, request, *args, **kwargs):
        value = {
            'object': models.State.get_first_state().to_dict(),
        }
        return JsonResponse(value)


class Upload(LoginRequiredMixin, FormView):
    """動画ファイルをアップロード
    """
    form_class = forms.UploadFileForm
    success_url = '/'
    template_name = 'root/upload.html'

    def get_form(self, form_class=None):
        form = super(Upload, self).get_form(form_class=form_class)
        form.fields['location'].choices = [(l.pk, l.name) for l in models.Location.objects.all()]
        return form

    def form_valid(self, form):
        bucket_name = settings.UPLOAD_S3_BUCKET_NAME
        file = self.request.FILES['file']
        temp_path = os.path.join(settings.BASE_DIR, 'tmp', file.name)
        with open(temp_path, 'wb+') as dest:
            [dest.write(c) for c in file.chunks()]

        s3_key = '{}/{}'.format(form.cleaned_data['location'], file.name)
        s3_upload_task.delay(bucket_name, s3_key, temp_path)
        return super(Upload, self).form_valid(form)


class UpdateState(LoginRequiredMixin, FormView):
    """状態を更新する
    """
    form_class = forms.UpdateStateForm
    template_name = 'root/upload.html'

    def get_form(self, form_class=None):
        form = super(UpdateState, self).get_form(form_class=form_class)
        form.fields['reason'].choices = models.Reason.get_choices_list(location_id=self.request.POST['location_id'])
        return form

    def form_invalid(self, form):
        print('form_invalid', form.errors)
        return JsonResponse(form.errors)

    def form_valid(self, form):
        state = models.State.objects.get(pk=form.cleaned_data['state_id'])
        state.update_state(
            form.cleaned_data['index'],
            form.cleaned_data['start_hour'],
            form.cleaned_data['start_minutes'],
            form.cleaned_data['start_sec'],
            form.cleaned_data['end_hour'],
            form.cleaned_data['end_minutes'],
            form.cleaned_data['end_sec'],
            form.cleaned_data['state_type'],
            form.cleaned_data['reason'],
        )
        state.save()
        value = state.get_state_list_json(dump=False)
        return JsonResponse(value)


class ControlIndex(LoginRequiredMixin, TemplateView):
    """
    コントロールパネルメニュー画面
    """
    template_name = "control/index.html"


class ControlUserList(LoginRequiredMixin, ListView):
    """
    ユーザー一覧
    """
    template_name = "control/user/list.html"
    model = models.User
    paginate_by = 30
    order_by = 'created'

    def get_queryset(self):
        queryset = super(ControlUserList, self).get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


class ControlUserRegist(LoginRequiredMixin, CreateView):
    """
    ユーザー登録
    """
    template_name = "control/user/regist.html"
    form_class = forms.UserCreationForm
    model = get_user_model()
    success_url = '/control/user/list'


class ControlUserUpdate(LoginRequiredMixin, UpdateView):
    """
    ユーザー情報更新
    """
    template_name = "control/user/update.html"
    form_class = forms.SelfUserChangeForm
    model = get_user_model()
    success_url = '/control/user/list'


class ControlUserDelete(LoginRequiredMixin, FormView):
    """
    ユーザー削除
    """
    form_class = forms.DeleteUser
    success_url = '/control/user/list'

    def form_valid(self, form):
        form.save()  # ユーサー削除処理
        return super(ControlUserDelete, self).form_valid(form)

    def get_initial(self):
        from django.contrib.auth import get_user_model
        pk = self.kwargs.get('pk')
        user = get_user_model().objects.get(pk=pk)
        return {'username': user.username}


class ControlLocationList(LoginRequiredMixin, ListView):
    """
    ロケーション一覧
    """
    template_name = "control/location/list.html"
    model = models.Location
    paginate_by = 30

    def get_queryset(self):
        queryset = super(ControlLocationList, self).get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


class ControlLocationRegist(LoginRequiredMixin, CreateView):
    """
    ロケーション登録
    """
    template_name = "control/location/regist.html"
    form_class = forms.LocationForm
    model = models.Location
    success_url = '/control/location/list'


class ControlLocationUpdate(LoginRequiredMixin, UpdateView):
    """
    ロケーション情報更新
    """
    template_name = "control/location/update.html"
    form_class = forms.LocationForm
    model = models.Location
    success_url = '/control/location/list'


class ControlLocationDelete(LoginRequiredMixin, FormView):
    """
    ロケーション削除
    """
    form_class = forms.DeleteLocation
    success_url = '/control/location/list'

    def form_valid(self, form):
        form.save()  # ユーサー削除処理
        return super(ControlLocationDelete, self).form_valid(form)


class ControlReasonList(LoginRequiredMixin, ListView):
    """
    変更理由一覧
    """
    template_name = "control/reason/list.html"
    model = models.Reason
    paginate_by = 30

    def get_context_data(self, *args, **kwargs):
        context_data = super(ControlReasonList, self).get_context_data(*args, **kwargs)
        context_data['location_id'] = self.kwargs.get('location_id')
        return context_data

    def get_queryset(self):
        queryset = super(ControlReasonList, self).get_queryset()
        location_id = self.kwargs.get('location_id')
        queryset = queryset.filter(location_id=location_id)
        return queryset


class ControlReasonRegist(LoginRequiredMixin, CreateView):
    """
    変更理由登録
    """
    template_name = "control/reason/regist.html"
    form_class = forms.ReasonForm
    model = models.Reason
    success_url = '/control/reason/list'

    def get_success_url(self):
        return reverse('app:control_reason_list', args=[self.kwargs.get('location_id')])

    def get_context_data(self, **kwargs):
        context_data = super(ControlReasonRegist, self).get_context_data(**kwargs)
        context_data['location_id'] = self.kwargs.get('location_id')
        return context_data

    def get_form(self, form_class=None):
        form = super(ControlReasonRegist, self).get_form(form_class=form_class)
        return form

    def get_initial(self):
        initial = super(ControlReasonRegist, self).get_initial()
        initial['location'] = self.kwargs.get('location_id')
        return initial


class ControlReasonUpdate(LoginRequiredMixin, UpdateView):
    """
    変更理由更新
    """
    template_name = "control/reason/update.html"
    form_class = forms.ReasonForm
    model = models.Reason
    success_url = '/control/reason/list'

    def get_success_url(self):
        return reverse('app:control_reason_list', args=[self.kwargs.get('location_id')])


class ControlReasonDelete(LoginRequiredMixin, FormView):
    """
    変更理由削除
    """
    form_class = forms.DeleteReasonForm
    success_url = '/control/reason/list'

    def get_success_url(self):
        return reverse('app:control_reason_list', args=[self.kwargs.get('location_id')])

    def form_valid(self, form):
        form.save()  # 削除処理
        return super(ControlReasonDelete, self).form_valid(form)


class ControlStateList(LoginRequiredMixin, ListView):
    """
    状態一覧
    """
    template_name = "control/state/list.html"
    model = models.State
    paginate_by = 30

    def get_queryset(self):
        queryset = super(ControlStateList, self).get_queryset()
        return queryset


class ControlStateRegist(LoginRequiredMixin, CreateView):
    """
    状態登録
    """
    template_name = "control/state/regist.html"
    form_class = forms.StateForm
    model = models.State
    success_url = '/control/state/list'


class ControlStateUpdate(LoginRequiredMixin, UpdateView):
    """
    状態情報更新
    """
    template_name = "control/state/update.html"
    form_class = forms.StateForm
    model = models.State
    success_url = '/control/state/list'
