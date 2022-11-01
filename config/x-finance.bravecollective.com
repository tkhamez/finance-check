# /etc/nginx/sites-available/x-finance.bravecollective.com

server {
    listen 80;
    server_name finance.bravecollective.com;

    location / {
        uwsgi_read_timeout 300;
        uwsgi_send_timeout 300;
        include uwsgi_params;
        uwsgi_pass unix:/opt/finance-check/web/app.sock;
    }
}
