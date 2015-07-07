#-*- coding:utf-8 -*-
from django.db import models

# Create your models here.

class supermasters(models.Model):
    '''主DNS'''
    ip = models.CharField(max_length=25)
    nameserver = models.CharField(max_length=255)
    account = models.CharField(max_length=40, null=True)

    def __unicode__(self):
        return self.nameserver

class logs(models.Model):
    '''DNS 日志'''
    id_server = models.IntegerField(max_length=11, default=0)
    id_domain = models.CharField(max_length=11, null=True)
    timestamp = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=30, null=True)
    cn_name = models.CharField(max_length=30, null=True)
    log_type = models.CharField(max_length=10, null=True)
    log_contents = models.TextField(max_length=1000, null=True)

    def __unicode__(self):
        return self.name

class users(models.Model):
    '''用户管理'''

    username = models.CharField(max_length=255)
    permission = models.CharField(max_length=255)

    def __unicode__(self):
        return self.username

class permission(models.Model):
    '''权限管理'''

    pid = models.CharField(max_length=20)
    permission = models.CharField(max_length=100)

    def __unicode__(self):
        return self.pid
