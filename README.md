# 部署说明

## 操作系统

- CentOS 7


## 2.安装软件

- Python 3.6.6
- Nginx 1.12.2
- Redis
- Mongo


## 安装 virtualenv

```bash
pip3 install virtualenv
cd
virtualenv -p /usr/local/python3.6/bin/python3.6 ENV3.6
source /home/kyapp/ENV3.6/bin/activate
pip install -r requirement.txt
```

## 修改配置
```
项目目录下修改 env 对应的数据库链接
根据实际环境修改 .env
gunicorn 配置在 config/gunicorn.py
```

# 启动服务

```bash
source /home/kyapp/ENV3.6/bin/activate
sh start.sh
```