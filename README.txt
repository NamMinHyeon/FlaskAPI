■ Environment ■

1. Gunicorn
 - ErrorLog path : /var/log/syslog
 - Install path : /usr/local/bin/Gunicorn
 - Flask(File) path : /etc/nginx/sites-enabled/Flask
 - gunicorn.service(File) path : /etc/systemd/system/gunicorn.service

2. Nginx → Gunicorn → [Socket] → Flask [wsgi.py (Entry Point) → app.py]

3. Start Option
 - sudo nginx -t		              : Nginx Env Check
 - sudo systemctl restart nginx : Nginx Env Restart

 - sudo systemctl start gunicorn.service   : Gunicorn Start
 - sudo systemctl enable gunicorn.service  : Required when restarting AWS EC2 server
 - sudo systemctl status gunicorn.service  : Gunicorn Status
 - sudo systemctl restart gunicorn.service : Gunicorn Restart (When the file exchanged)
 - sudo systemctl stop gunicorn.service    : Gunicorn Stop
 - sudo systemctl daemon-reload            : Required when the 'gunicorn.service' file change

 4. Source File path
 - /home/ubuntu/project/Flask

5. Packages
 - pip install -r requirements.txt