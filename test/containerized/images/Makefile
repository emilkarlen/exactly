IMAGES = 36 37 38 39 310 311
DOCKER_FILES = $(foreach img,$(IMAGES),Dockerfile.$(img))
IMAGE_PFX = exactly-alpine-py
IMAGES__FULL_NAME = $(foreach img,$(IMAGES),$(IMAGE_PFX)$(img))

.PHONY: $(IMAGES) dockerfiles all clean help

help:
	@echo help all clean $(IMAGES) dockerfiles $(DOCKER_FILES)

all: $(IMAGES)

clean:
	rm -f $(DOCKER_FILES)
	docker image rm -f $(IMAGES__FULL_NAME)

dockerfiles: $(DOCKER_FILES)

Dockerfile.36: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.6-alpine/g' < Dockerfile.in > $@

Dockerfile.37: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.7-alpine/g' < Dockerfile.in > $@

Dockerfile.38: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.8-alpine/g' < Dockerfile.in > $@

Dockerfile.39: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.9-alpine/g' < Dockerfile.in > $@

Dockerfile.310: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.10-alpine/g' < Dockerfile.in > $@

Dockerfile.311: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.11-alpine/g' < Dockerfile.in > $@


36: Dockerfile.36
	docker build -f Dockerfile.36 -t $(IMAGE_PFX)36 .

37: Dockerfile.37
	docker build -f Dockerfile.37 -t $(IMAGE_PFX)37 .

38: Dockerfile.38
	docker build -f Dockerfile.38 -t $(IMAGE_PFX)38 .

39: Dockerfile.39
	docker build -f Dockerfile.39 -t $(IMAGE_PFX)39 .

310: Dockerfile.310
	docker build -f Dockerfile.310 -t $(IMAGE_PFX)310 .

311: Dockerfile.311
	docker build -f Dockerfile.311 -t $(IMAGE_PFX)311 .
