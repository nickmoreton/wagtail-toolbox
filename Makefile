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

coverage:
	@echo "Running coverage..."
	@coverage report
