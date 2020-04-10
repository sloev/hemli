test: build_service_image build_test_image
	docker-compose -f integration_tests/docker-compose.testing.yml \
	  up --build \
	  --force-recreate \
	  --renew-anon-volumes
	#   --abort-on-container-exit \
	#   #--exit-code-from integration_tests

build_test_image:
	@echo ____BUILDING TEST IMAGE____
	docker build -f integration_tests/Dockerfile.testing -t integration_tests --cache-from integration_tests .

build_service_image:
	@echo ____BUILDING HEMLI API IMAGE____
	docker build -f web/Dockerfile -t hemli_api --cache-from hemli_api --cache-from sloev/travis-build-cache:latest .

lint: 
	black .

lintcheck:
	black --check .

ci: lintcheck test