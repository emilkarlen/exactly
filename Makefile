PHONY=help clean dist install uninstall upload upload-test venv
NON_PHONY=venv-run venv-build
ALL=$(PHONY) $(NON_PHONY)

.PHONY: $(PHONY)

help:
	@echo $(ALL)

clean:
	rm -rf dist
	rm -rf src/exactly.egg-info

dist:
	python3 -m build --no-isolation

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
    pip install --upgrade wheel; \
    pip install --upgrade build;

venv: venv-run venv-build
