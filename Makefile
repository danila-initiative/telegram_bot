start-container-rebuild:
	docker-compose up -d --build

start-container-demon:
	docker-compose up -d

enter-container-rebuild: start-container-rebuild
	docker exec -it bot_zakupki_telegram-bot_1 bash

enter-container: start-container-demon
	docker exec -it bot_zakupki_telegram-bot_1 bash

check-pep8:
	flake8 bot_zakupki & mypy bot_zakupki

smart-format:
	black --line-length 79  bot_zakupki tests

test:
	bash /app/runtests.sh

enter-rebuild-production-container:
	docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d --build
	docker exec -it bot_zakupki_telegram-bot_1 bash