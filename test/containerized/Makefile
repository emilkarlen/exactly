VERSIONS = 36 37 38 39 310 311

.PHONY: help images all $(VERSIONS)

help:
	@echo help  $(VERSIONS) all

images:
	make -C images all

all: $(VERSIONS)

36:
	$(CURDIR)/run -v 36 test-w-install
37:
	$(CURDIR)/run -v 37 test-w-install
38:
	$(CURDIR)/run -v 38 test-w-install
39:
	$(CURDIR)/run -v 39 test-w-install
310:
	$(CURDIR)/run -v 310 test-w-install
311:
	$(CURDIR)/run -v 311 test-w-install
