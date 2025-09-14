# Easy Bundle Creation

[TOC]

## Introduction

Easy Bundle Creation is a backend service that accepts RPC calls, creates the
factory bundles and supports downloading the created bundles.

To see the full prerequisites and setup, check go/cros-bundle-creator-setup.

## File location

### ChromeOS repository

* `$(factory-repo)/py/bundle_creator` contains the main codebase.
* `$(factory-repo)/deploy/bundle_creator.sh` is the helper script to
  deploy the project.
* `$(factory-private-repo)/config/bundle_creator` contains all the
  confidential configurations.


## Development Guide

### Prerequisites

Install Docker
  - go/installdocker

Install dependencies:
```
sudo apt-get install protobuf-compiler google-cloud-sdk
```

### Build & Deploy

To deploy the app engines, run:

```
(factory-repo)$ ./deploy/bundle_creator.sh deploy-appengine-v2 ${deployment_type}
(factory-repo)$ ./deploy/bundle_creator.sh deploy-appengine-legacy ${deployment_type}
```

To deploy the compute engine, run:

```
(factory-repo)$ ./deploy/bundle_creator.sh deploy-docker ${deployment_type}
```

To create Pub/Sub's topic and subscription used by the app engine and the
compute engine, run:
```
(factory-repo)$ ./deploy/bundle_creator.sh create-pubsub ${deployment_type}
```

To access the VM, run:
```
# SSH into the VM
(factory-repo)$ ./deploy/bundle_creator.sh ssh-vm ${deployment_type}

# Login the docker
(inside VM)$ docker exec -it bundle-docker-1 sh
```

### Testing

#### Unittest

`make -C $(factory-repo) test` ignores all unittest modules related to Easy
Bundle Creation. Instead, developers should trigger the tests by the helper
script as follow:

```
(factory-repo)$ ./deploy/bundle_creator.sh test-appengine-v2
(factory-repo)$ ./deploy/bundle_creator.sh test-docker
```

The `test-test-appengine-v2` command trigger the tests under
`./py/bundle_creator/app_engine_v2` and some scripts under
`./py/bundle_creator/connector`.

The `test-docker` command trigger the tests under `./py/bundle_creator/docker`
and `./py/bundle_creator/connector`.

#### Manual test

To run `docker/worker.py` in local, run:
```
(factory-repo)$ ./deploy/bundle_creator.sh run-docker ${deployment_type}
```

### Sending request

```
(factory-repo)$ cat > /tmp/create_bundle.txt << EOF
email: "$(whoami)@google.com"
bundle_metadata {
  board: "cherry"
  project: "tomato"
  phase: "pvt"
  toolkit_version: "14195.0.0"
  test_image_version: "14195.0.0"
  release_image_version: "14195.0.0"
}
hwid_option {
  update_db_firmware_info: 0
}
EOF
(factory-repo)$ ./deploy/bundle_creator.sh request ${deployment_type} < /tmp/create_bundle.txt
```
