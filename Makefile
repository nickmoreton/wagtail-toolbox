# WAGTAIL
migrate:
	@echo "Migrating database..."
	@python manage.py migrate

migrations:
	@echo "Making migrations..."
	@python manage.py makemigrations

server:
	@echo "Running server..."
	@python manage.py runserver 0:8000

superuser:
	@echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', '', 'admin')" | python manage.py shell

test:
	@echo "Running tests..."
	@coverage run manage.py test
	@coverage report

coverage:
	@echo "Running coverage..."
	@coverage report

# MANAGEMENT COMMAND SORTCUTS
inspect-post:
	@python manage.py inspector wordpress.WPPost

inspect-post-signatures:
	@python manage.py inspector wordpress.WPPost --signatures

inspect-page:
	@python manage.py inspector wordpress.WPPage

inspect-page-signatures:
	@python manage.py inspector wordpress.WPPage --signatures

import-all:
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/users WPAuthor
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/categories WPCategory
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/tags WPTag
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/pages WPPage
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/posts WPPost
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/media WPMedia
	@python manage.py importer http://localhost:8888/wp-json/wp/v2/comments WPComment

# WORDPRESS
wp-setup:
	./setup.sh

wp-up:
	docker-compose up -d

wp-init:
	docker-compose exec wordpress bash -c "bin/init.sh"

wp-down:
	docker-compose down

wp-destory:
	docker-compose down -v
