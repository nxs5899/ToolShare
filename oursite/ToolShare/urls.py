from django.conf.urls import url
from .views import views, shed_views, admin_views, report_views, user_views
#from .views import reports

app_name = 'ToolShare'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?i)tools/$', views.view_tools, name='tools'),
    url(r'^(?i)my-tools/$', views.view_mytools, name='my-tools'),
    url(r'^(?i)register-tool/$', views.register_tool, name='register-tool'),
    url(r'^(?i)shed/borrow/(?P<toolId>\d+)/$',views.view_borrow_tool, name='borrow-tool'),
    url(r'^(?i)my-tools/tool-update/(?P<toolId>\d+)/$',views.view_update_tool, name='tool-update'),
    url(r'^(?i)shed-tools/$', views.view_shed_tools, name='shed-tools'),
    url(r'^(?i)shed/return-tools/$', views.view_return_tools, name='return-tool'),
    url(r'^(?i)shed/shed-update/(?P<shedid>\d+)/$',shed_views.update_shed, name='tool-shed'),
    url(r'^(?i)notifications/$',views.show_notification, name='view-notifications'),
    url(r'^(?i)my-tools/blackout-tool/(?P<toolId>\d+)/$',views.view_blackout_tool, name='blackout-tool'),
    url(r'^(?i)request/(?P<requestId>\d+)/$',views.ApproveRequest , name='Approve-Request'),
    url(r'^(?i)ack-return/(?P<requestId>\d+)/$',views.view_acknowledge_tool_return , name='acknowledge-tool-return'),


    #User Page URLs
    url(r'^(?i)register-user/$', user_views.add_user, name='register-user'),
    url(r'^(?i)signin/$', user_views.signin, name='signin'),
    url(r'^(?i)myprofile/$', user_views.update_user, name='myprofile'),
    url(r'^(?i)logout/$', 'django.contrib.auth.views.logout', {'next_page': '/ToolShare/signin'}, name='logout'),
    url(r'^(?i)password-change/$', user_views.passwordchange, name='password-change'),
    url(r'^(?i)register-user-status/$', user_views.user_status, name='register-user-status'),
    url(r'^(?i)exit-sharezone/$',user_views.view_exit_sharezone, name='exit-sharezone'),

    #Report Page URLs
    url(r'^(?i)report/most-active-borrowers/$', report_views.most_active_borrowers, name='active-borrowers'),
    url(r'^(?i)report/most-active-lenders/$', report_views.most_active_lenders, name='active-lenders'),
    url(r'^(?i)report/most-borrowed-tools/$', report_views.most_borrowed_tools, name='most-borrowed'),
    url(r'^(?i)report/current-borrowed-tools/$', report_views.recent_tools, name='current-borrowed'),
    url(r'^(?i)report/tool-history/$', report_views.tool_history, name='tool-history'),
    url(r'^(?i)report/user-history/$', report_views.user_history, name='user-history'),

    #Admin Page URLs
    url(r'^(?i)admin/manage-tools/$', admin_views.view_delete_tools, name='admin-manage-tools'),
    url(r'^(?i)admin/add-edit-tool/$', admin_views.add_edit_tool, name='admin-add-edit-tool'),
    url(r'^(?i)admin/restore-tool/$', admin_views.restore_tool, name='admin-restore-tool'),
    url(r'^(?i)admin/manage-share_zones/$', admin_views.view_delete_share_zones, name='admin-manage-share_zones'),
    url(r'^(?i)admin/add-edit-share_zone/$', admin_views.add_edit_share_zone, name='admin-add-edit-share_zone'),
    url(r'^(?i)admin/manage-sheds/$', admin_views.view_delete_sheds, name='admin-manage-sheds'),
    url(r'^(?i)admin/add-edit-shed/$', admin_views.add_edit_shed, name='admin-add-edit-shed'),
    url(r'^(?i)admin/manage-users/$', admin_views.view_delete_users, name='admin-manage-users'),
    url(r'^(?i)admin/add-edit-user/$', admin_views.add_edit_user, name='admin-add-edit-user'),
    url(r'^(?i)admin/restore-user/$', admin_views.restore_user, name='admin-restore-user'),
    url(r'^(?i)admin/create-admin/$', admin_views.create_admin, name='admin-create'),
    url(r'^(?i)admin/view-admins/$', admin_views.view_admins, name='admin-view'),
    url(r'^(?i)admin/edit-admin/$', admin_views.edit_admin, name='admin-edit'),
    url(r'^(?i)admin/password-reset/(?P<userId>\d+)/$', admin_views.password_reset, name='admin-password-reset'),
    url(r'^(?i)admin/error/$', admin_views.error, name='admin-error'),
]

