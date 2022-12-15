
VERSION ?=dev

.PHONY: docker
docker:
	docker buildx build --build-arg VERSION=$(VERSION) -t jumpserver/applets:$(VERSION) .
