IMAGES = alpine-py35 alpine-py36 alpine-py37 alpine-py38 alpine-py39
.PHONY: $(IMAGES)

all: $(IMAGES)

clean:
	docker image rm -f $(IMAGES)

alpine-py35:
	docker build -f alpine-py/Dockerfile.35 -t alpine-py35 alpine-py

alpine-py36:
	docker build -f alpine-py/Dockerfile.36 -t alpine-py36 alpine-py

alpine-py37:
	docker build -f alpine-py/Dockerfile.37 -t alpine-py37 alpine-py

alpine-py38:
	docker build -f alpine-py/Dockerfile.38 -t alpine-py38 alpine-py

alpine-py39:
	docker build -f alpine-py/Dockerfile.39 -t alpine-py39 alpine-py
