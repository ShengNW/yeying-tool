
# 添加静态文件

1. 将静态文件拷贝到目录/usr/share/nginx/html/static, 比如添加privacy-policy.html文件
2. 在nginx配置中添加映射
# Static files
location /privacy-policy.html {
  alias /usr/share/nginx/html/static/privacy-policy.html;
}
3. 修改文件所有者确保nginx能够访问，通常nginx的启动用户是www-data
```shell
chown www-data:www-data privacy-policy.html
```
4. 重启nginx服务


# 常见问题

检查DNS解析是否正常：
nslookup <domain name>

检查域名端口限制：
nc -zv <domain name> 443
