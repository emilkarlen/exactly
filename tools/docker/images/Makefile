DOCKER_FILES = Dockerfile.35 Dockerfile.36 Dockerfile.37 Dockerfile.38 Dockerfile.39

all: $(DOCKER_FILES)

clean:
	rm -f $(DOCKER_FILES)

Dockerfile.35: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.5.9-alpine/g' < Dockerfile.in > $@

Dockerfile.36: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.6-alpine3.11/g' < Dockerfile.in > $@

Dockerfile.37: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.7-alpine3.12/g' < Dockerfile.in > $@

Dockerfile.38: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.8-alpine3.11/g' < Dockerfile.in > $@

Dockerfile.39: Dockerfile.in
	sed 's/__IMAGE_TAG__/3.9-rc-alpine3.11/g' < Dockerfile.in > $@
