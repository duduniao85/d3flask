common 文件夹包含一组辅助函数以满足你的应用程序公共的需求。例如，它也可能包含任何自定义输入/输出类型
models 文件夹包含了基于 sqlalchemy的orm后台数据表对象
resources 文件夹包含了对外暴露的资源
flask rest-api 参考相应的地址    http://www.pythondoc.com/Flask-RESTful/quickstart.html
启动方式：
myvenv\Scripts\activate
python manage.py runserver --host 0.0.0.0

#单独测试指定定时任务的方法
myvenv\Scripts\activate   生产环境使用  source myvenv/Scripts/activate
python manage.py shell
from common.tasks import crawlDailyQuote
crawlDailyQuote()
source ./myvenv/Scripts/activate
exit()
python manage.py shell
from common.tasks import crawlLianjiaChengjiao
crawlLianjiaChengjiao(app)
from common.tasks import main
#单独测试后台表结构建立是否合理
python manage.py shell

#生产启动gunicorn
pkill python
pkill gunicorn

cd /var/www/d3flask
gunicorn -w4 -b 0.0.0.0:8000 manage:app

#生产编辑nginx目录
/alidata/server/nginx/conf/vhosts
service nginx restart

#生产需要额外处理的程序包
lxml
cx_oracle
包需要单独处理

#生成新的requirements
pip freeze > requirements.txt
#根据requirements 安装更新
pip install -r requirements.txt