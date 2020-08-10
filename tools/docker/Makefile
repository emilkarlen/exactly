IMAGES = alpine-py35 alpine-py36 alpine-py37 alpine-py38 alpine-py39
all: $(IMAGES)

.PHONY: $(IMAGES)

alpine-py35:
	docker build -f alpine-py3/Dockerfile.35 -t alpine-py35 alpine-py3

alpine-py36:
	docker build -f alpine-py3/Dockerfile.36 -t alpine-py36 alpine-py3

alpine-py37:
	docker build -f alpine-py3/Dockerfile.37 -t alpine-py37 alpine-py3

alpine-py38:
	docker build -f alpine-py3/Dockerfile.38 -t alpine-py38 alpine-py3

alpine-py39:
	docker build -f alpine-py3/Dockerfile.39 -t alpine-py39 alpine-py3

clean:
	docker image rm -f $(IMAGES)
