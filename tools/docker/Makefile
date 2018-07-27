IMAGES = linux-py3
all: $(IMAGES)

.PHONY: $(IMAGES)

linux-py3:
	docker build -t linux-py3 linux-py3

clean:
	docker image rm -f $(IMAGES)
