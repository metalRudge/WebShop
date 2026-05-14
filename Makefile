tailwind:
	tailwindcss -i ./src/input.css -o ./src/output.css --watch

run:
	python manage.py runserver
shell:
	python manage.py shell
migrate:
	python manage.py migrate
makemigrations:
	python manage.py makemigrations
check:
	python manage.py shell -c "from MyShop.models import Product; print(Product.objects.all())"