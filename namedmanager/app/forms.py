#-*- coding:utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from app.models import users
import re

class AddRecordForm(forms.Form):
    id = forms.CharField(required=False)
    type = forms.CharField(widget=forms.Select)
    content = forms.CharField(error_messages={'required': u'记录值不能为空'})
    ttl = forms.CharField(error_messages={'required': u'TTL值不能为空'})
    prio = forms.CharField(required=False)
    hostname = forms.CharField(error_messages={'required': u'主机记录不能为空'})
    domain = forms.CharField(error_messages={'required': u'域名不能为空'})

    def clean_content(self):
        content = self.cleaned_data['content']
        type = self.cleaned_data['type']
        if type == "A":
            pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            rst = pat.match(content)
            if not rst:
                raise ValidationError(u'IP地址格式不正确,请重新输入.')
        return content 

    def clean_ttl(self):
        ttl = self.cleaned_data['ttl']
        pat = re.compile("^\d+")
        rst = pat.match(ttl)
        if not rst:
            raise ValidationError(u'TTL格式不正确,请重新输入')
        return ttl

    def clean(self):
        return self.cleaned_data

class AddUserForm(forms.Form):
    username = forms.CharField(error_messages={'required': u'用户名不能为空'})
    permissions = forms.CharField(error_messages={'required': u'请选择权限'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if users.objects.filter(username='%s' % username).first():
           raise ValidationError(u'该用户已经存在')  
        return username

    def clean(self):
        return self.cleaned_data
