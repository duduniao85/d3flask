common �ļ��а���һ�鸨���������������Ӧ�ó��򹫹����������磬��Ҳ���ܰ����κ��Զ�������/�������
models �ļ��а����˻��� sqlalchemy��orm��̨���ݱ����
resources �ļ��а����˶��Ⱪ¶����Դ
flask rest-api �ο���Ӧ�ĵ�ַ    http://www.pythondoc.com/Flask-RESTful/quickstart.html
������ʽ��
myvenv\Scripts\activate
python manage.py runserver --host 0.0.0.0

#��������ָ����ʱ����ķ���
myvenv\Scripts\activate   ��������ʹ��  source myvenv/Scripts/activate
python manage.py shell
from common.tasks import crawlDailyQuote
crawlDailyQuote()
source ./myvenv/Scripts/activate
exit()
python manage.py shell
from common.tasks import crawlLianjiaChengjiao
crawlLianjiaChengjiao(app)
from common.tasks import main
#�������Ժ�̨��ṹ�����Ƿ����
python manage.py shell

#��������gunicorn
pkill python
pkill gunicorn

cd /var/www/d3flask
gunicorn -w4 -b 0.0.0.0:8000 manage:app

#�����༭nginxĿ¼
/alidata/server/nginx/conf/vhosts
service nginx restart

#������Ҫ���⴦��ĳ����
lxml
cx_oracle
����Ҫ��������

#�����µ�requirements
pip freeze > requirements.txt
#����requirements ��װ����
pip install -r requirements.txt