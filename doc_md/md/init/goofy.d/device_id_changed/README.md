**source code:** [init/goofy.d/device\_id\_changed/README.md](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/init/goofy.d/device_id_changed/README.md)

# Chrome OS Factory scripts when Device ID changed.

Script here will be executed when a device ID change is detected,
executed by `/usr/local/factory/init/goofy.d/device_id.sh`.

To add your own service, create a script file with `.sh` in file name extension
and enable execute (+x) permission.

Usually this is done by adding a file in private board overlay, for example
`src/private-overlays/overlay-coral-private/chromeos-base/factory-board/files/init/goofy.d/device_id_changed/reset_something.sh`
that the `reset_something` must be a simple shell script.
