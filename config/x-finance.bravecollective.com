# /etc/nginx/sites-available/x-finance.bravecollective.com

server {
    listen 80;
    server_name finance.bravecollective.com;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/opt/finance-check/web/app.sock;
    }
}
