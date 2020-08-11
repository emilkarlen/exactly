IMAGES = alpine-py35 alpine-py36 alpine-py37 alpine-py38 alpine-py39
.PHONY: $(IMAGES) dockerfiles

all: $(IMAGES)

clean:
	docker image rm -f $(IMAGES)

dockerfiles:
	$(MAKE) -C images

alpine-py35: dockerfiles
	docker build -f images/Dockerfile.35 -t alpine-py35 images

alpine-py36: dockerfiles
	docker build -f images/Dockerfile.36 -t alpine-py36 images

alpine-py37: dockerfiles
	docker build -f images/Dockerfile.37 -t alpine-py37 images

alpine-py38: dockerfiles
	docker build -f images/Dockerfile.38 -t alpine-py38 images

alpine-py39: dockerfiles
	docker build -f images/Dockerfile.39 -t alpine-py39 images
