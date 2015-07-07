from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^login.html', 'app.views.Login'),
    url(r'^main.html', 'app.views.main'),
    url(r'^adddomain.html', 'app.views.adddomain'),
    url(r'^records.html', 'app.views.records'),
    url(r'^addrecord.html', 'app.views.add_record'),
    url(r'^recorddel.html', 'app.views.del_record'),
    url(r'^recordchange.html', 'app.views.add_record'),
    url(r'^logs.html', 'app.views.logs_record'),
    url(r'^user.html', 'app.views.user_manager'),
    url(r'^adduser.html', 'app.views.adduser'),
    url(r'^userdel.html', 'app.views.userdel'),
    url(r'^logout.html', 'app.views.logout'),
    url(r'^$', 'app.views.main'),
)
