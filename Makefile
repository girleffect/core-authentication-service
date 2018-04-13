VENV=./ve
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
FLAKE8=$(VENV)/bin/flake8
DB_NAME=authentication_service
DB_USER=authentication_service

# Colours.
CLEAR=\033[0m
RED=\033[0;31m
GREEN=\033[0;32m
CYAN=\033[0;36m

.SILENT: docs-build
.PHONY: check test

help:
	@echo "usage: make <target>"
	@echo "    $(CYAN)build-virtualenv$(CLEAR): Creates virtualenv directory, 've/', in project root."
	@echo "    $(CYAN)clean-virtualenv$(CLEAR): Deletes 've/' directory in project root."
	@echo "    $(CYAN)docs-build$(CLEAR): Build documents and place html output in docs root."

$(VENV):
	@echo "$(CYAN)Initialise base ve...$(CLEAR)"
	virtualenv $(VENV) -p python3.6
	@echo "$(GREEN)DONE$(CLEAR)"

# Creates the virtual environment.
build-virtualenv: $(VENV)
	@echo "$(CYAN)Building virtualenv...$(CLEAR)"
	$(VENV)/bin/pip install -r requirements/requirements.txt
	@echo "$(GREEN)DONE$(CLEAR)"

# Deletes the virtual environment.
clean-virtualenv:
	@echo "$(CYAN)Clearing virtualenv...$(CLEAR)"
	rm -rf $(VENV)
	@echo "$(GREEN)DONE$(CLEAR)"

# Build sphinx docs, then move them to docs/ root for GitHub Pages usage.
docs-build:  $(VENV)
	@echo "$(CYAN)Installing Sphinx requirements...$(CLEAR)"
	$(PIP) install sphinx sphinx-autobuild
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Backing up docs/ directory content...$(CLEAR)"
	tar -cvf backup.tar docs/source docs/Makefile
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Clearing out docs/ directory content...$(CLEAR)"
	rm -rf docs/
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Restoring base docs/ directory content...$(CLEAR)"
	tar -xvf backup.tar
	@echo "$(GREEN)DONE$(CLEAR)"
	# Remove the tar file.
	rm backup.tar
	# Actually make html from index.rst
	@echo "$(CYAN)Generating sphinx sources...$(CLEAR)"
	$(VENV)/bin/sphinx-apidoc --separate --private --force -o docs/source authentication_service authentication_service/management authentication_service/migrations authentication_service/tests authentication_service/admin.py authentication_service/celery.py  authentication_service/constants.py
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Generating sphinx docs...$(CLEAR)"
	$(MAKE) -C docs/source clean html SPHINXBUILD=../../$(VENV)/bin/sphinx-build
	@echo "$(GREEN)DONE$(CLEAR)"
	@echo "$(CYAN)Moving build files to docs/ root...$(CLEAR)"
	cp -r docs/_build/html/. docs/
	rm -rf docs/_build/
	@echo "$(GREEN)DONE$(CLEAR)"

prism:
	curl -L https://github.com/stoplightio/prism/releases/download/v0.6.21/prism_linux_amd64 -o prism
	chmod +x prism

mock-authentication-service-api: prism
	./prism run --mockDynamic --list -s swagger/authentication_service.yml -p 8012

validate-swagger: prism
	@./prism validate -s swagger/authentication_service.yml && echo "The Swagger spec contains no errors"

$(FLAKE8): $(VENV)
	$(PIP) install flake8

check: $(FLAKE8)
	$(FLAKE8)

database:
	sql/create_database.sh $(DB_NAME) $(DB_USER) | sudo -u postgres psql -f -

test:
	$(PYTHON) manage.py test --settings=authentication_service.tests.settings.111

authentication-service-api: $(VENV)
	$(VENV)/bin/pip install -r $(VENV)/src/swagger-django-generator/requirements.txt
	$(PYTHON) $(VENV)/src/swagger-django-generator/swagger_django_generator/generator.py swagger/authentication_serv

make-translations:
	@echo "$(CYAN)Generating .po files...$(CLEAR)"
	mkdir other_packages
	cp -r ./ve/lib/python3.6/site-packages/oidc_provider ./other_packages
	cp -r ./ve/lib/python3.6/site-packages/two_factor ./other_packages
	django-admin makemessages --all -i "ve/*"
	rm -rf other_packages
	@echo "$(GREEN)DONE$(CLEAR)"

translate:
	@echo "$(CYAN)Compiling translation files...$(CLEAR)"
	django-admin compilemessages
	@echo "$(GREEN)DONE($CLEAR)"
