Steps to run project

Step1: create virtual env with command -> python3 -m venv venv
Step2: Activate that virtualenv -> source venv/bin/activate
Step3: Install all the requirements -> pip install -r requirements.txt
Step4: Set Up the Database -> python manage.py makemigrations -> python manage.py migrate
Step5: Run Project -> python3 manage.py runserver 5000
Step6: Run Background Job Command -> celery -A bankingsystem beat --loglevel=info
