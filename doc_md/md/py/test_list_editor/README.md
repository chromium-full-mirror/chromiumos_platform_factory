**source code:** [py/test\_list\_editor/README.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test_list_editor/README.md)

# Test List Editor

## Folder Structure

* The `backend/` folder holds the code related to the backend.
* The `frontend/` folder holds the code related to the frontend.

## System Architecture

We will create a nginx instance to serve the frontend static files. The nginx instance will
also act as a reverse proxy to direct the traffic to the backend.
