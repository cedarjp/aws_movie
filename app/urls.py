from django.urls import path
from app import views

app_name = 'app'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('state/', views.State.as_view(), name='state'),
    path('detail/<pk>', views.Detail.as_view(), name='detail'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('update_state/', views.UpdateState.as_view(), name='update_state'),
    path('control/', views.ControlIndex.as_view(), name='control_index'),
    path('control/user/list', views.ControlUserList.as_view(), name='control_user_list'),
    path('control/user/regist', views.ControlUserRegist.as_view(), name='control_user_regist'),
    path('control/user/update/<pk>', views.ControlUserUpdate.as_view(), name='control_user_update'),
    path('control/user/delete/<pk>', views.ControlUserDelete.as_view(), name='control_user_delete'),
    path('control/location/list', views.ControlLocationList.as_view(), name='control_location_list'),
    path('control/location/regist', views.ControlLocationRegist.as_view(), name='control_location_regist'),
    path('control/location/update/<pk>', views.ControlLocationUpdate.as_view(), name='control_location_update'),
    path('control/location/delete/<pk>', views.ControlLocationDelete.as_view(), name='control_location_delete'),
    path('control/reason/list/<int:location_id>', views.ControlReasonList.as_view(), name='control_reason_list'),
    path('control/reason/regist/<int:location_id>', views.ControlReasonRegist.as_view(), name='control_reason_regist'),
    path('control/reason/update/<int:location_id>/<int:pk>', views.ControlReasonUpdate.as_view(), name='control_reason_update'),
    path('control/reason/delete/<int:location_id>/<int:pk>', views.ControlReasonDelete.as_view(), name='control_reason_delete'),
    path('control/state/list', views.ControlStateList.as_view(), name='control_state_list'),
    path('control/state/regist', views.ControlStateRegist.as_view(), name='control_state_regist'),
    path('control/state/update/<pk>', views.ControlStateUpdate.as_view(), name='control_state_update'),
]
