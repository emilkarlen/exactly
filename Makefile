ALL = clean build build_deb_sdist build_deb_bdist install uninstall36 uninstall-venv upload upload-test

.PHONY: $(ALL)
help:
	@echo $(ALL)

clean:
	rm -rf build
	rm -rf dist deb_dist
	rm -rf src/exactly.egg-info


build:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

# Build for Debian using python3-stdeb
build_deb_sdist:
	python3 setup.py --command-packages=stdeb.command sdist_dsc

# Build for Debian using python3-stdeb
build_deb_bdist:
	python3 setup.py --command-packages=stdeb.command bdist_deb



install:
	python3 setup.py install

uninstall36:
	test -d /usr/local/lib/python3.6/site-packages/exactly-*-py3.6.egg && rm -rf  /usr/local/lib/python3.6/site-packages/exactly-*-py3.6.egg
	test -f /usr/local/bin/exactly && rm -f /usr/local/bin/exactly

uninstall-venv:
	-test -d venv/lib/python*/site-packages/exactly*.egg && rm -rf  venv/lib/python*/site-packages/exactly*.egg
	-test -f venv/bin/exactly && rm -f venv/bin/exactly


upload:
	python3 -m twine upload dist/*

upload-test:
	python3 -m twine upload --repository pypitest dist/*
