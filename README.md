docker build -t zakup_admin_bot .   

docker run --rm -d --name zakup_admin_container zakup_admin_bot
docker run --rm --name zakup_admin_container zakup_admin_bot

docker exec -it zakup_bot_telegram-bot_1 bash  

docker-compose --env-file ./.env up --build

tail -f /var/log/cron.log

30 7 * * * /usr/local/bin/python3 /code/src/parser_demon.py >> /code/logs/log.log 2>&1
0 8 * * * /usr/local/bin/python3 /code/src/admin_bot_broadcast.py >> /code/logs/log.log 2>&1