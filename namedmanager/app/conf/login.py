#!/usr/bin/env python
#-*- coding:utf8 -*-

import ldap
from config import LDAP_SERVER, BASE_DN

def check_credentials(username, password):
    SERVER = LDAP_SERVER
    LDAP_USERNAME = '%s@david.com' % username
    LDAP_PASSWORD = password
    DN = BASE_DN
    LDAP_FILTER = "sAMAccountName=%s" % username
    retrieveAttributes = None
    
    try:
        conn = ldap.initialize(SERVER)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
    except ldap.INVALID_CREDENTIALS:
        conn.unbind()
        rst = {'status': '502',
               'method': '/login.html',
               'message': '用户名或密码输入有误!'}
        return rst
    except ldap.SERVER_DOWN:
        rst = {'status': '504',
               'method': '/login.html',
               'message': 'LDAP 连接失败,请发送邮件至davidbjhd@gmail.com'}
        return rst

    id = conn.search(DN, ldap.SCOPE_SUBTREE, LDAP_FILTER, retrieveAttributes)
    data = conn.result(id, 0)
    rst = {'status': '200',
           'action': 'POST',
           'method': '/main.html',
           'message': {
                'mail': data[1][0][1]['mail'][0],
                'cn_name': data[1][0][1]['name'][0],
                'name': data[1][0][1]['sAMAccountName'][0]}
        }
    return rst
