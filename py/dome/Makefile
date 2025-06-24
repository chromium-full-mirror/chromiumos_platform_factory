# Copyright 2012 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

define DOME_MAKE_HELP_MESSAGE
Usage: $(MAKE) TARGET

Targets:
  lint           lint both back-end and front-end files
  lint-backend   lint back-end files
  lint-frontend  lint front-end files
  test           run back-end and front-end end-to-end tests
  test-backend   run back-end end-to-end tests
  test-frontend  run front-end end-to-end tests
endef
export DOME_MAKE_HELP_MESSAGE

DOME_DIR=/usr/local/factory/py/dome
TEMP_DOCKER_HOST_IP=172.18.0.10
TEMP_DOME_E2E_DIR=/tmp/dome_e2e
TEMP_UMPIRE=umpire_fake_correct_project_name
TEMP_SECONDARY_UMPIRE=umpire_fake_secondary
TEMP_UMPIRE_EXIST=$(shell docker ps --format {{.Names}} | grep ${TEMP_UMPIRE})
TEMP_SECONDARY_UMPIRE_EXIST=$(shell docker ps \
	--format {{.Names}} | grep ${TEMP_SECONDARY_UMPIRE})

# Command used to analyze test coverage in target 'test-backend'.
TEST_COVERAGE_CMD = \
	mkdir /tmp/shared && \
	coverage run \
		--source="." \
		--omit="backend/migrations/*" \
		manage.py test && \
	coverage report && \
	coverage html --directory="build/test_coverage_report"

.PHONY: help lint-backend lint-frontend test-backend test-frontend

all: help

help:
	@echo "$${DOME_MAKE_HELP_MESSAGE}"

lint: lint-backend lint-frontend

lint-backend:
	make -C ../.. lint \
		LINT_FILES="py/dome/backend/*.py py/dome/backend/migrations/*.py"

lint-frontend:
	../../setup/cros_docker.sh build
	docker run --rm cros/dome-builder npm run lint
	touch .lint-frontend-passed

test: test-frontend test-backend
	touch .tests-passed

test-backend:
	../../setup/cros_docker.sh build
	# TODO(b/34117401): remove hard-coded path
	docker run \
		--rm \
		--volume "$(CURDIR)/../../build/docker:/usr/local/factory/py/dome/build" \
		--volume "/cros_docker/dome/test_log:/var/log/dome" \
		--workdir "${DOME_DIR}" \
		cros/factory_server \
		sh -c "$(TEST_COVERAGE_CMD)"

test-frontend:
	echo "Running dome frontend test"
	../../setup/cros_docker.sh build
	docker run --rm cros/dome-builder npm run test

test-frontend-coverage:
	echo "Running dome frontend test coverage"
	docker rm -f dome_builder
	../../setup/cros_docker.sh build
	docker run --name dome_builder cros/dome-builder npm run test:coverage
	docker cp "dome_builder:${DOME_DIR}/frontend/report" "$(CURDIR)/frontend/"
	docker rm dome_builder

e2e-test:
	echo "Running dome frontend e2e test"
	[ -d "${TEMP_DOME_E2E_DIR}" ] && \
		sudo rm -r "${TEMP_DOME_E2E_DIR}" || echo "${TEMP_DOME_E2E_DIR} not found."
	if [ -n "$(TEMP_UMPIRE_EXIST)" ]; then \
		docker stop "${TEMP_UMPIRE}" && docker rm "${TEMP_UMPIRE}"; \
	fi
	if [ -n "$(TEMP_SECONDARY_UMPIRE_EXIST)" ]; then \
		docker stop "${TEMP_SECONDARY_UMPIRE}" && \
		docker rm "${TEMP_SECONDARY_UMPIRE}"; \
	fi
	ps -eaf | grep -i 'shopfloor' | grep -v grep | \
		awk '{print $$2}' | xargs -r kill
	HOST_SHARED_DIR="${TEMP_DOME_E2E_DIR}" ../../setup/cros_docker.sh dev run
	../../bin/factory_env python3 ../../py/shopfloor/shopfloor_service.py \
		-p 8091 & sudo sh -c "echo $$! > ${TEMP_DOME_E2E_DIR}/shopfloor.pid"
	docker run --network dome-dev-network --ip ${TEMP_DOCKER_HOST_IP} \
		--rm cros/dome-builder npm run e2e
	kill `cat ${TEMP_DOME_E2E_DIR}/shopfloor.pid`
	../../setup/cros_docker.sh dev destroy
	touch .e2e-tests-passed
