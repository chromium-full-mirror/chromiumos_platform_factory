# Dome User Guide

Dome: The Factory Server Management Console

## Introduction to Dome

Dome is our new factory management console. On the factory server side, we have
different projects responsible for different parts before: Shopfloor, Umpire,
Instalog, etc. They all have their own ways to manage, and require knowledge of
the command line interface. Therefore, Dome was born: management console for
all things in just one place, and best of all, it's GUI. In the future, you no
longer need to set up Shopfloor, Umpire, or Instalog independently. You set up
Dome, and let Dome help you finish all the tasks for you.

## Prerequisite

1. You need [Docker](http://docker.io) installed on the target computer. Read
   [Factory Server](../../setup/FACTORY_SERVER.md#Prerequisite) for more
   details.

2. Dome is a web-based program, if you want to use it on the same Linux
   machine running Dome, you’ll need the desktop environment. Run following
   commands to install the desktop environment and Chromium browser:

   ```shell
   sudo apt-get install ubuntu-desktop chromium-browser
   ```

## Installation

Dome is one of the component bundled in Chrome OS Factory Server package, so
please follow the steps in
[Factory Server](../../setup/FACTORY_SERVER.md#Installation) to deploy and
install Dome.

### Access Dome Web User Interface

Open your browser to port 8000 of the Dome server, and you should see the
welcome page. For example, if you're using the same machine and had the desktop
environment set up, open the browser to `http://localhost:8000`.

The default login credential is `admin / test0000`. The password can be
changed by running command `./cros_docker.sh passwd`.

*** note
**Note**: using Chrome/Chromium is highly recommended. If you want to use other
browsers such as Firefox, you'll have to make sure the timeout setting is long
enough or you're likely to get an timeout error when uploading bundle files
since they're normally very large.
***

### Using Dome
TBD.


### How to Enable HTTPS on DOME (Factory Server)

Because Dome is open source, we cannot provide the private key on source code.
If you want to enable HTTPS on DOME, you can use your certificate files.

Here's a brief instruction to enable HTTPS:
- Create a `ssl.conf` file under `/cros_docker/dome` folder.
- Modify this `ssl.conf` file, you need to add these configurations:
  ```
  listen  443 ssl;

  ssl_certificate  /var/db/factory/dome/nginx/certificate.crt;
  ssl_certificate_key  /var/db/factory/dome/nginx/private.key;
  ```
- Put your `certificate.crt` and `private.key` files into `/cros_docker/dome/nginx`
  folder.
- Run `setup/cros_docker.sh run`.
- Now you can visit to [https://localhost:8001](https://localhost:8001).

### How to Enable HTTPS on Umpire

Here's a brief instruction to enable HTTPS on Umpire side:
- Create a `protocol.json` file under `/cros_docker/dome` folder.
- Modify this `protocol.json` file. If you want to use HTTPS on Umpire side,
  add the json string like following:
  ```
  {
    "use_https": true
  }
  ```
- Put your `selfsigned.crt` and `selfsigned.key` files into `/cros_docker/dome`
  folder. Note: Please use `selfsigned.crt` and `selfsigned.key` as the filename.
- Run `setup/cros_docker.sh run`.
- For the first time we change from HTTP to HTTPS, we need to delete all umpire
  projects and create them again for now.

---

### Run E2E Testing of Dome

1. Run following command under `py/dome` to run the e2e test.

       make e2e-test
