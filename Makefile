PHONY=help clean dist doc ref-man install uninstall upload upload-test venv
NON_PHONY=venv-run venv-build
ALL=$(PHONY) $(NON_PHONY)

.PHONY: $(PHONY)

help:
	@echo $(ALL)
	@echo
	@echo 'Run make from the project root directory.'

clean:
	rm -rf dist
	rm -rf build
	rm -rf src/exactly.egg-info

dist:
	python3 -m build --no-isolation

doc:
	make -f sphinx.mak html

build:
	mkdir build

ref-man: build
	python3 src/default-main-program-runner.py help htmldoc > build/exactly.html

install:
	python3 -m pip install dist/*.whl

uninstall:
	python3 -m pip uninstall --yes exactly

upload:
	python3 -m twine upload dist/*

upload-test:
	python3 -m twine upload --repository PyPiTest dist/*

venv-run:
	python3 -m venv venv-run

venv-build:
	python3 -m venv venv-build
	. venv-build/bin/activate; \
    pip --require-virtualenv install --upgrade -r build-requirements.txt

venv: venv-run venv-build
