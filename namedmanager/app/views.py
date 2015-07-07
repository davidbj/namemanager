#-*- coding:utf-8 -*-

import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from app.db import model
from app.conf import config
from app.conf.config import NS_IP1, NS_IP2
from app.forms import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from app.conf import login
from functools import wraps
from app.models import logs, permission, users, permission
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def is_login(func):
    @wraps(func)
    def _is_login(req, *args, **kwargs):
        data = func(req, *args, **kwargs)
        if data['status'] == '200' and data['action'] == 'GET':
            return render(req, data['method'])
        elif data['status'] == '200' and data['action'] == 'POST':
            req.session['name'] = data['message']['name'] 
            req.session['cn_name'] = data['message']['cn_name']
            return HttpResponseRedirect(data['method'])
        elif data['status'] == '502':
            return HttpResponse('<script>alert("%s");location.replace("%s")</script>' % (data['message'], data['method']))
        elif data['status'] == '504':
            return HttpResponse('<script>alert("%s");location.replace("%s")</script>' % (data['message'], data['method']))
    return _is_login

def check_is_login(func):
    @wraps(func)
    def _check_is_login(req, *args, **kwargs):
        try:
            name = req.session['name']
        except Exception:
            name = ''
        if name:
            return func(req, *args, **kwargs)
        else:
            return HttpResponseRedirect('/login.html')
    return _check_is_login

@is_login
def Login(req):
    if req.method == "POST":
        user = req.POST.get('username')
        password = req.POST.get('password')
        data = login.check_credentials(user, password)
        return data
    else:
        data = {'status':'200', 'action':'GET', 'method': 'login.html'}
        return data

@check_is_login
def main(req):
    if req.method == "GET":
        db = connDb()
        tmp = db.select('select * from domains')
        domain_ld =[]
        for i in tmp:
            domain_ld.append(i[1])

        #Rights management
        pms = [ i.encode('ascii') for i in permission_manager(req.session['name']).split(',')]
        p_obj = permission.objects.filter(permission='add_domain').first()
        pid = p_obj.pid.encode('ascii')

        return render(req, 'main.html', {'domain_ld': domain_ld, 'status': '0', 'pms':pms, 'pid':pid})

@check_is_login
def adddomain(req):
    db = connDb()
    if req.method == "GET":
        t_domains = req.GET.get('domain')
        try:
            #add record domain table.
            db.insert('domains', {'name':t_domains, 'type':'MASTER'}) 
            db.commit()

            #Query domain_id record
            domain_id_obj = db.select("select id from domains where name='%s'" % t_domains)
            domain_id = domain_id_obj[0][0]
            
            #add SOA record
            db.insert('records', {'domain_id': domain_id, 'name': t_domains, 'type': 'SOA', 'ttl': 600, 'hidden': 1, 'content': 'ns1.%s admin.%s %s' % (t_domains, t_domains, get_domain_version()), 'change_date': get_now_time()}) 
            db.commit()

            #add NS record
            db.insert('records', {'domain_id': domain_id, 'name': t_domains, 'type': 'NS', 'ttl': 600, 'change_date': get_now_time(), 'hostname': '@', 'hidden': 2, 'content': 'ns1.%s' % t_domains})
            db.commit()

            db.insert('records', {'domain_id': domain_id, 'name': t_domains, 'type': 'NS', 'ttl': 600, 'change_date': get_now_time(), 'hostname': '@', 'hidden': 2, 'content': 'ns2.%s' % t_domains})
            db.commit()

            #add A record
            db.insert('records', {'domain_id': domain_id, 'name': 'ns1.%s' % t_domains, 'type': 'A', 'content': '%s' % NS_IP1, 'ttl': 600, 'change_date': get_now_time(), 'hostname': 'ns1'})
            db.commit()

            db.insert('records', {'domain_id': domain_id, 'name': 'ns2.%s' % t_domains, 'type': 'A', 'content': '%s' % NS_IP2, 'ttl': 600, 'change_date': get_now_time(), 'hostname': 'ns2'})
            db.commit()

            try:
                w_logs('domains', 'insert', domain=t_domains, tp='MASTER', name=req.session['name'], cn_name=req.session['cn_name'])
            except Exception, e:
                print e

            domain = json.dumps({'status':'200'})
        except Exception as e:
            print e
            domain = json.dumps({'status':'500'})
    return HttpResponse(domain)


@check_is_login
def records(req):
    if req.method == "GET":
        db = connDb()
        domain = req.GET.get('domain')

        tmp = db.select('select * from domains')
        domain_ld =[]

        for i in tmp:
            domain_ld.append(i[1])

        if domain:
            data = {}
            ld = []
            ns_data = {}
            ns_ld = []

            try:
                domain_id = db.select('select id from domains where name="%s"' % domain)
                records = db.select('select * from records where domain_id="%s" and hidden="0"' % domain_id[0])
                ns_records = db.select('select * from records where domain_id="%s" and hidden="2"' % domain_id[0])
            except Exception:
                return render(req, '500.html')

            for record in records:
                data['id'] = record[0]
                data['hostname'] = record[8]
                data['type'] = record[3]
                data['content'] = record[4]
                data['ttl'] = record[5]
                if record[6] == None:
                    data['prio'] = ''
                else:
                    data['prio'] = record[6]
                ld.append(data)
                data = {}

            for ns_record in ns_records:
                ns_data['id'] = ns_record[0]
                ns_data['hostname'] = ns_record[8]
                ns_data['type'] = ns_record[3]
                ns_data['content'] = ns_record[4]
                ns_data['ttl'] = ns_record[5]
                if ns_record[6] == None:
                    ns_data['prio'] = ''
                ns_ld.append(ns_data)
                ns_data = {}

            record_type_tuple = db.select('select type from record_type')
            record_type = []
            for type in record_type_tuple:
                record_type.append(type[0].encode('ascii'))

        #Rights management
        pms = [ i.encode('ascii') for i in permission_manager(req.session['name']).split(',')]

        #add record
        add_record_obj = permission.objects.filter(permission='add_record').first()
        add_record = add_record_obj.pid.encode('ascii')

        #delete record
        del_record_obj = permission.objects.filter(permission='delete_record').first()
        del_record = del_record_obj.pid.encode('ascii')

        #update record
        update_record_obj = permission.objects.filter(permission='update_record').first()
        update_record = update_record_obj.pid.encode('ascii')

        try:    
            return render(req, 'record.html', {'records': ld, 'domain': domain, 'record_type': record_type, 'domain_ld':domain_ld, 'ns_records': ns_ld, 'status': '0', 'pms': pms, 'add_record': add_record, 'del_record': del_record, 'update_record': update_record})
        except Exception, e:
            return render(req, '500.html') 

@csrf_exempt
def add_record(req):
    ''' 
        1. 添加和更新记录.
        2. id大于0,则更新记录.
    '''
    if req.method == "POST":
        forms = AddRecordForm(req.POST)
        if forms.is_valid():
            id = forms.cleaned_data['id']
            type = forms.cleaned_data['type'] 
            content = forms.cleaned_data['content']
            ttl = forms.cleaned_data['ttl']
            prio = forms.cleaned_data['prio']
            hostname = forms.cleaned_data['hostname']
            name = forms.cleaned_data['domain']
            domain_id = get_domain_id(name)
            change_date = get_now_time()
            if type.lower() != "mx" and type.lower() != "ns" and type.lower() != "soa" and type.lower() != "txt" and hostname != '@':
                name = '.'.join([hostname, name])
            if not id:
                try:
                    db = connDb()
                    db.insert('records', {'domain_id': domain_id, 'name': name, 'content': content, 'ttl': ttl, 'prio': prio, 'change_date': change_date, 'hostname': hostname, 'type': type})
                    db.commit()
                    data= json.dumps({'status': '200'})
                    try:
                        w_logs('records', 'insert', domain=name, tp=type, name=req.session['name'], cn_name=req.session['cn_name'], domain_id=domain_id, content=content, ttl=ttl, prio=prio, hostname=hostname, change_date=change_date)
                    except Exception, e:
                        print e

                    return HttpResponse(data)
                except Exception, e:
                    data = json.dumps({'status':'500', 'err': e})
                    return HttpResponse(data)
            else:
                try:
                    db = connDb()
                    db.update('records', {'domain_id': domain_id, 'name': name, 'content': content, 'ttl': ttl, 'prio': prio, 'change_date': change_date, 'hostname': hostname, 'type': type}, {'id': id})
                    db.commit()
                    data = json.dumps({'status': '200'})
                    try:
                        w_logs('records', 'update', domain=name, tp=type, name=req.session['name'], cn_name=req.session['cn_name'], domain_id=domain_id, content=content, ttl=ttl, prio=prio, hostname=hostname, change_date=change_date, id=id)
                    except Exception, e:
                        print e
                    return HttpResponse(data)
                except Exception, e:
                    data = json.dumps({'status': '500', 'err': e})
                    return HttpResponse(data)
        else:
            data = json.dumps({'status': '502', 'forms': u'格式输入有误~'})
            return HttpResponse(data)

@csrf_exempt
def del_record(req):
    if req.method == "POST":
        id = req.POST.get('id')
        try:
            db = connDb()
            db.delete('records', {'id': id})
            db.commit()
            data = json.dumps({'status': 200})
            try:
                w_logs('records', 'delete', name=req.session['name'], cn_name=req.session['cn_name'], id=id)
            except Exception, e:
                print e
            return HttpResponse(data)
        except Exception, e:
            data = json.dumps({'status': 500})
            return HttpResponse(data)

@check_is_login            
def logs_record(req):
    if req.method == "GET":
        domain = req.GET.get('domain')
        page = req.GET.get('page')
        db = connDb()
        tmp = db.select('select * from domains')
        domain_ld =[]
        for i in tmp:
            domain_ld.append(i[1])

        #分页
        limit = 10
        if domain:
            db = connDb()
            domain_id = db.select('select id from domains where name="%s"' % domain)
            domain_id = domain_id[0][0]
            log_record = logs.objects.filter(id_domain='%s' % domain_id).order_by('-timestamp').all()[:100]
            paginator = Paginator(log_record, limit)
            try:
                topics = paginator.page(page)
            except PageNotAnInteger:
                topics = paginator.page(1)
            except EmptyPage:
                topics = paginator.page(paginator.num_pages)
            return render(req, 'logs.html', {'log_record': log_record, 'domain': domain, 'domain_ld': domain_ld, 'log_status': '0', 'topics': topics})
        else:
            log_record = logs.objects.order_by('-timestamp').all()[:100]
            paginator = Paginator(log_record, limit)
            try:
                topics = paginator.page(page)
            except PageNotAnInteger:
                topics = paginator.page(1)
            except EmptyPage:
                topics = paginator.page(paginator.num_pages)

            return render(req, 'logs.html', {'log_record': log_record, 'domain': '-', 'domain_ld': domain_ld, 'log_status': '0', 'topics': topics})

@check_is_login
def user_manager(req):
    if req.method == "GET":
        permissions =  permission.objects.all()

        us = users.objects.all()
        ld = []
        us_ld = []
        for user in us:
            for pid in user.permission.split(','):
                t = permission.objects.filter(pid='%s' % pid).first()
                ld.append(t.permission)
                t = ''
            us_ld.append({'id': user.id,'username': user.username, 'permission': ','.join(ld)})
            ld=[]

        db = connDb()
        tmp = db.select('select * from domains')
        domain_ld =[]
        for i in tmp:
            domain_ld.append(i[1])

        #Rights management
        pms = [ i.encode('ascii') for i in permission_manager(req.session['name']).split(',')]

        #user manager
        user_manager_obj = permission.objects.filter(permission='user_manager').first()
        user_manager = user_manager_obj.pid.encode('ascii')
        return render(req, 'user.html', {'permissions': permissions, 'us': us_ld, 'domain_ld': domain_ld, 'user_status': '0', 'pms': pms, 'user_manager': user_manager})

@csrf_exempt
def userdel(req):
    if req.method == "POST":
        id = req.POST.get('id')
        try:
            user_id = users.objects.filter(id='%s' % id).first()
            user_id.delete()
            data = json.dumps({'status': 200})
            return HttpResponse(data)
        except Exception, e:
            data = json.dumps({'status': 500, 'err': u'用户删除失败，语法错误...'})
            return HttpResponse(data)

@check_is_login
def logout(req):
    if req.method == "GET":
        del req.session['name']
        del req.session['cn_name']
        return HttpResponseRedirect('/login.html') 

@csrf_exempt
def adduser(req):
    if req.method == "POST":
        forms = AddUserForm(req.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            permissions = forms.cleaned_data['permissions'] 
            try:
                add_user = users() 
                add_user.username = username
                add_user.permission = permissions
                add_user.save()
                data = json.dumps({'status': '200'})
                return HttpResponse(data)
            except Exception, e:
                data = json.dumps({'status': '500', 'err': e})
                return HttpResponse(data)
        else:
            data = json.dumps({'status': '502', 'forms': u'格式输入有误~'})
            return HttpResponse(data)

def connDb():
    db = model.DB(False, host=config.HOST, user=config.USER, passwd=config.PASSWD, db=config.DB)
    return db

def get_domain_id(domain):
    db = connDb()
    domain_id = db.select('select id from domains where name="%s"' % domain)
    return domain_id[0][0]

def get_now_time():
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute
    second = now.second
    date = '-'.join([str(year), str(month), str(day)])
    time = ':'.join([str(hour), str(minute), str(second)])
    date_time = ' '.join([date, time])
    return date_time

def w_logs(table, type, *args, **kwargs):
    w_log = logs()
    w_log.name = kwargs['name'] 
    w_log.cn_name = kwargs['cn_name']
    w_log.timestamp = get_now_time()
    
    if type.lower() == 'insert' and table.lower() == 'domains':
        w_log.log_contents = 'insert into %s (`name`,`type`) VALUES (%s, %s)' % (table, kwargs['domain'], kwargs['tp'])  
    elif type.lower() == 'insert' and table.lower() == 'records':
        if not kwargs['prio']:
            kwargs['prio'] = ''
        w_log.id_domain = kwargs['domain_id']
        w_log.log_type = kwargs['tp'] 
        w_log.log_contents = "insert into %s (`domain_id`, `name`, `type`, `content`, `ttl`, `prio`, `change_date`, `hostname`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" % (table, kwargs['domain_id'], kwargs['domain'], kwargs['tp'], kwargs['content'], kwargs['ttl'], kwargs['prio'], kwargs['change_date'], kwargs['hostname'])
    elif type.lower() == 'update' and table.lower() == 'records':
        if not kwargs['prio']:
            kwargs['prio'] = ''
        
        w_log.id_domain = kwargs['domain_id']
        w_log.log_type = kwargs['tp'] 
        w_log.log_contents = "update  %s  set domain_id='%s', name='%s', type='%s', content='%s', ttl='%s', prio='%s',change_date='%s', hostname='%s' where id='%s'" % (table, kwargs['domain_id'], kwargs['domain'], kwargs['tp'], kwargs['content'], kwargs['ttl'], kwargs['prio'], kwargs['change_date'], kwargs['hostname'], kwargs['id'])

    elif type.lower() == 'delete' and table.lower() == 'records':
        w_log.log_contents = "delete from %s where id='%s'" % (table, kwargs['id'])
    w_log.save()

def permission_manager(username):
    user_obj = users.objects.filter(username='%s' % username).first()
    pms = user_obj.permission 
    return pms
    
def get_domain_version():
    date_obj = datetime.now()
    version = ''.join([str(date_obj.day), str(date_obj.month), str(date_obj.day), str(date_obj.hour), str(date_obj.minute), str(date_obj.second)])
    return version
