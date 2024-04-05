VENV=venv-install
INSTALL_TOOL=python3 ../tools/install.py

PHONY=help clean repo-py repo-xly install-py containerized images
NON_PHONY=$(VENV)
ALL=$(PHONY) $(NON_PHONY)

.PHONY:$(PHONY)


# !!! KEEP IN SYNC WITH - Makefile.rst - !!! #


help:
	@echo Targets: $(ALL)
	@echo
	@echo 'See make.rst for more help.'

repo-py:
	python3 run-test-suite.py

repo-xly:
	python3 ../src/default-main-program-runner.py suite exactly-cases

containerized: images
	make -C containerized all

install-py: $(VENV)
	. $(VENV)/bin/activate; \
	$(INSTALL_TOOL) --venv install; \
	python3 run-test-suite-towards-installed-program.py; \
	$(INSTALL_TOOL) --venv uninstall;

images:
	make -C containerized images

$(VENV):
	python3 -m venv $@

clean:
	rm -rf $(VENV)
