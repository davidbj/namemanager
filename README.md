##NamedManager 是什么？
一个管理powerdns记录的平台。

##NamedManager 有哪些功能？
* 方便管理PowerDns的domain、record、record Type、ttl等.
* 用户审计功能。

##平台搭建
* pdns 及pdns-recursor 安装
    * yum install pdns pdns-backend-mysql pdns-recursor
* pdns 及 pdns-recursor 配置管理
    * pdns 配置文件  
    `vim /etc/pdns/pdns.conf`
        setuid=pdns   
        setgid=pdns  
        launch=bind  
        recursor=127.0.0.1:5300     `recursor监听ip:port`    
        soa-refresh-default=7200  
        launch=gmysql              
        gmysql-host=`x.x.x.x`       `#mysql的地址`  
        gmysql-user=db_manager      `#连接mysql的用户名`   
        gmysql-password=`password`   
        gmysql-dbname=powerdns     

    * pdns-recursor 配置文件   
    `vim /etc/pdns-recursor/recursor.conf`
        setuid=pdns-recursor   
        setgid=pdns-recursor  
        forward-zones=david.com=172.16.10.206   `#访问*.david.com domain record的转发至172.16.10.206 这台dns Server.`  
        local-port=5300        
    
    
* 启动服务   
    /etc/init.d/pdns-recursor start    
    /etc/init.d/pdns start   
    chkconfig pdns-recursor on  
    chkconfig pdns on   

##NamadManager 搭建
* nginx安装与配置  
  * yum install nginx
  * pdns.conf 配置文件
    `vim /etc/nginx/conf.d/pdns.conf`
     
    server {
        listen 80;
        server_name dns.david.com;
        access_log /var/log/nginx/dns.david.com.log main;
        charset utf-8;
        location /static {
            alias /data/namdmanager/app/static/;
            index index.html index.htm;
        }

        location / {
            uwsgi_pass  x.x.x.x:8000;
            include uwsgi_params;
        }
    }
    
* uwsgi安装与配置
  * pip install uwsgi
  * uwsgi.ini 配置文件
    `详件namedmanager目录下uwsgi.ini配置文件`

* Django需要的第三方插件
    backports.ssl-match-hostname==3.4.0.2   
    configobj==4.7.2   
    decorator==3.4.0   
    iniparse==0.4    
    pycurl==7.19.0  
    pygobject==3.8.2  
    pygpgme==0.3  
    pyliblzma==0.5.3  
    pyudev==0.15  
    pyxattr==0.5.1  
    slip==0.4.0  
    slip.dbus==0.4.0  
    urlgrabber==3.10  
    virtualenv==12.0.7  
    wsgiref==0.1.2  
    yum-metadata-parser==1.1.4  
* 启动服务
  `启动uwsgi`
  cd /data/namedmanager && uwsgi named_uwsgi.ini
* 启动nginx
  systemctl start nginx (centos7)


##有问题反馈
在使用中有任何问题，欢迎返回给我，可以用以下联系方式跟我交流

* 邮件(davidbjhd#gmail.com, 把#换成@)
* QQ: 782112501
* twitter: [@david_bj0](https://twitter.com/david_bj0)
* blog: http://davidbj.blog.51cto.com

## 关于作者
```javascript
   var Author = {
       nickName : "david",
       site : "http://davidbj.blog.51cto.com"  
   }

```
