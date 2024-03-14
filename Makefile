ALL=help clean dist install uninstall upload upload-test venv

.PHONY: $(ALL)

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

venv:
	python3 -m venv venv
