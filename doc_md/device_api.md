# Device-Aware API and Board

If you need to implement test behavior for device (DUT or station) in a
board-specific way, use or extend
[`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard).  This class provides
board-specific functionality, e.g.:

- forcing device charge state
- observing on-board sensors such as temperature sensors
- querying the EC (embedded controller)
- directly reading/writing values over the I2C bus

## Obtaining a Board object

To obtain a [`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard) object for
the device under test, use the following function:

<a id="module-cros.factory.device.device_utils"></a>

### cros.factory.device.device_utils.CreateDUTInterface(\*\*options)

Returns a Device board interface from DUT config.

### cros.factory.device.device_utils.CreateStationInterface(\*\*options)

Returns a Device board interface from Station config.

<a id="board-api-extending"></a>

## Extending the Board class

The base implementation of all boards is
[`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard). Currently if
board_class is not specified, device_utils.CreateDUTInterface() function will
return an instance of interface for ChromeOS devices using the subclass
`cros.factory.device.boards.chromeos.ChromeOSBoard`.  However, you may
find that you need to customize or override certain functionality for your
project. To do so:

1. Define a new subclass of
   `cros.factory.device.boards.chromeos.ChromeOSBoard`
   in the `cros.factory.device.boards` package.  In general,
   for a board named `*xxx*`, you will add a
   file `private-overlays/overlay-*xxx*-private/chromeos-base/factory-board/files/py/device/boards/*xxx*.py`
   containing the following:
   ```default
   from cros.factory.device.boards import chromeos
   from cros.factory.device import device_types
   from cros.factory.utils import type_utils


   # Implement or import and override the components with difference.
   class XxxPower(types.DeviceComponent):

     def DoSomething(self):
       pass


   class XxxBoard(chromeos.ChromeOSBoard):
     # ... implement/override methods here ...

     @type_utils.Overrides
     @types.DeviceProperty
     def power(self):
       return XXXPower(self)
   ```

   Generally, your class should be derived from the
   `cros.factory.device.boards.chromeos.ChromeOSBoard` class, but
   if your device is not ChromeOS, you may wish to directly subclass
   `cros.factory.device.boards.android.AndroidBoard` or
   [`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard).
2. Specify that your implementation should be used.  To do this, in
   `private-overlays/overlay-*board*-private/chromeos-base/factory-board/files/py/config/devices.json`,
   write a JSON configuration to specify the type of board and link to use just
   like the following:
   ```default
   {"dut": {"board_class": "XXXBoard", "link_class": "XXXLink"}}
   ```

   board_class refers to the class name under cros.factory.device.boards,
   and link_class refers to the class name under cros.factory.device.links.

## Adding new modules to the Board class

If you need to perform some system operation in a highly CrOS-specific
or board-specific way, you may need to add a new property or method to the
[`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard) class.

Let’s say that you’re working on a cool new CrOS device (“mintyfresh”)
with a built-in air freshener, and you need to write a test for this
game-changing new component.  Consider the following questions:

- **Is there a mostly standard way of controlling the air freshener
  across CrOS devices, but that might be different for certain
  devices?** (For instance, you can call `ectool airfreshener 1` to
  enable the air freshener, but CrOS devices with a non-standard EC
  may need to implement this differently.)

  In this case, add an abstract module `airfreshener.py` to
  `cros.factory.device` and include that in
  [`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard) as a new
  DeviceProperty `airfreshener`.
  it will work for “standard” devices but can be overridden as necessary.
- **Is the functionality totally one-off for your device?** (For instance,
  you need to control the device via a hard-coded register on the I2C bus.)

  If so, add an abstract method to
  [`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard) and provide the
  implementation directly in your
  `cros.factory.device.boards.mintyfresh.MintyFreshBoard` class.
  Don’t provide an implementation in
  `cros.factory.device.boards.chromeos.ChromeOSBoard`, since
  it wouldn’t be useful on other boards anyway.
- **Is the functionality confidential?**

  If so, simply implement your functionality in
  `cros.factory.device.boards.mintyfresh.MintyFreshBoard`.
  Once the device is launched, add a method to
  [`cros.factory.device.device_types.DeviceBoard`](#cros.factory.device.device_types.DeviceBoard) and move your
  implementation to
  `cros.factory.device.boards.chromeos.ChromeOSBoard` so it
  can be re-used for future devices.

## API Documentation

### *class* cros.factory.device.device_types.DeviceBoard(link: [IDeviceLink](#cros.factory.device.device_types.IDeviceLink))

A base class all for board implementations to inherit from.

#### Call(\*args, \*\*kargs) → int

Executes a command on target device, using subprocess.call convention.

The arguments are explained in Popen.

Do not override this function. The behavior of this function depends on the
underlying device (e.g. SSH-connected device or local device), which has
been well-handled by Popen.

* **Returns:**
  Exit code from executed command.

#### CallOutput(\*args, \*\*kargs) → None | bytes | str

Runs the command on device and returns standard output if success.

Do not override this function. The behavior of this function depends on the
underlying device (e.g. SSH-connected device or local device), which has
been well-handled by Popen.

* **Returns:**
  If command exits with zero (success), return the standard output;
  otherwise None. If the command didn’t output anything then the result is
  empty string.

#### CheckCall(command: str | Sequence[str], stdin: None | int | IO[Any] = None, stdout: None | int | IO[Any] = None, stderr: None | int | IO[Any] = None, cwd: str | None = None, log=False) → int

Executes a command on device, using subprocess.check_call convention.

Do not override this function. The behavior of this function depends on the
underlying device (e.g. SSH-connected device or local device), which has
been well-handled by Popen.

* **Parameters:**
  * **command** – A string or a list of strings for command to execute.
  * **stdin** – A file object to override standard input.
  * **stdout** – A file object to override standard output.
  * **stderr** – A file object to override standard error.
  * **cwd** – The working directory for the command.
  * **log** – True (for logging.info) or a logger object to keep logs before
    running the command.
* **Returns:**
  Exit code from executed command, which is always 0.
* **Raises:**
  **CalledProcessError if the exit code is non-zero.** – 

#### CheckOutput(command: str | Sequence[str], stdin: None | int | IO[Any] = None, stderr: None | int | IO[Any] = None, cwd: str | None = None, log=False, , encoding: str | None = 'utf-8') → str | bytes

Executes a command on device, using subprocess.check_output convention.

Do not override this function. The behavior of this function depends on the
underlying device (e.g. SSH-connected device or local device), which has
been well-handled by Popen.

* **Parameters:**
  * **command** – A string or a list of strings for command to execute.
  * **stdin** – A file object to override standard input.
  * **stderr** – A file object to override standard error.
  * **cwd** – The working directory for the command.
  * **log** – True (for logging.info) or a logger object to keep logs before
    running the command.
  * **encoding** – The name of the encoding used to decode the command’s output.
    Set to `None` to read as byte.
* **Returns:**
  The output on STDOUT from executed command.
* **Raises:**
  **CalledProcessError if the exit code is non-zero.** – 

#### *abstractmethod* GetStartupMessages()

Get various startup messages.

This is usually useful for debugging issues like unexpected reboot during
test.

Returns: a dict that contains logs.

#### Glob(pattern: str) → List[str]

Finds files on target device by pattern, similar to glob.glob.

* **Parameters:**
  **pattern** – A file path pattern (allows wild-card ‘\*’ and ‘?).
* **Returns:**
  A list of files matching pattern on target device.

#### IsReady()

Returns True if a device is ready for access.

This is usually simply forwarded to `link.IsReady()`, but some devices may
need its own readiness check in additional to link layer.

#### Popen(command: str | Sequence[str], stdin: None | int | IO[Any] = None, stdout: None | int | IO[Any] = None, stderr: None | int | IO[Any] = None, cwd: str | None = None, log=False, encoding: str | None = 'utf-8') → Popen

Executes a command on target device using subprocess.Popen convention.

Compare to subprocess.Popen, the argument shell=True/False is not
available for this function.  When command is a list, it treats each
item as a command to be invoked.  When command is a string, it treats
the string as a shell script to invoke.

* **Parameters:**
  * **command** – A string or a list of strings for command to execute.
  * **stdin** – A file object to override standard input.
  * **stdout** – A file object to override standard output.
  * **stderr** – A file object to override standard error.
  * **cwd** – The working directory for the command.
  * **log** – True (for logging.info) or a logger object to keep logs before
    running the command.
  * **encoding** – Same as subprocess.Popen, we will use utf-8 as default to make
    it output str type.
* **Returns:**
  An object similar to subprocess.Popen.

#### ReadFile(path: str, count: int | None = None, skip: int | None = None) → str

Returns file contents on target device.

By default the “most-efficient” way of reading file will be used, which may
not work for special files like device node or disk block file. Use
ReadSpecialFile for those files instead.

Meanwhile, if count or skip is specified, the file will also be fetched by
ReadSpecialFile.

* **Parameters:**
  * **path** – A string for file path on target device.
  * **count** – Number of bytes to read. None to read whole file.
  * **skip** – Number of bytes to skip before reading. None to read from beginning.
* **Returns:**
  A string as file contents.

#### ReadSpecialFile(path: str, count: int | None = None, skip: int | None = None, encoding: str | None = 'utf-8')

Returns contents of special file on target device.

Reads special files (device node, disk block, or sys driver files) on device
using the most portable approach.

* **Parameters:**
  * **path** – A string for file path on target device.
  * **count** – Number of bytes to read. None to read whole file.
  * **skip** – Number of bytes to skip before reading. None to read from beginning.
  * **encoding** – The encoding of the file content.
* **Returns:**
  A string or bytes as file contents.

#### SendDirectory(local: str, remote: str) → None

Copies a local directory to target device.

local should be a local directory, and remote should be a non-existing
file path on target device.

Example:

```default
SendDirectory('/path/to/local/dir', '/remote/path/to/some_dir')
```

Will create directory some_dir under /remote/path/to and copy
files and directories under /path/to/local/dir/ to some_dir.

* **Parameters:**
  * **local** – A string for directory path in local.
  * **remote** – A string for directory path on remote device.

#### SendFile(local: str, remote: str) → None

Copies a local file to target device.

* **Parameters:**
  * **local** – A string for file path in local.
  * **remote** – A string for file path on remote device.

#### WriteFile(path: str, content: str) → None

Writes some content into file on target device.

* **Parameters:**
  * **path** – A string for file path on target device.
  * **content** – A string to be written into file.

#### WriteSpecialFile(path: str, content: str) → None

Writes some content into a special file on target device.

* **Parameters:**
  * **path** – A string for file path on target device.
  * **content** – A string to be written into file.

#### accelerometer

Sensor measures proper acceleration (also known as g-sensor).

#### ambient_light_sensor

Ambient light sensors.

#### audio

Audio input and output, including headset, mic, and speakers.

#### bluetooth

Interface to connect and control Bluetooth devices.

#### camera

Interface to control camera devices.

#### display

Interface for showing images or taking screenshot.

#### ec

Module for controlling Embedded Controller.

#### fan

Module for fan control.

#### gyroscope

Gyroscope sensors.

#### hwmon

Hardware monitor devices.

#### i2c

Module for accessing to target devices on I2C bus.

#### info

Module for static information about the system.

#### init

Module for adding / removing start-up jobs.

#### led

Module for controlling LED.

#### magnetometer

Magnetometer / Compass.

#### memory

Module for memory information.

#### partitions

Provide information of partitions on a device.

#### path

Provides operations on path names, similar to os.path.

#### power

Interface for reading and controlling battery.

#### status

Returns live system status (dynamic data like CPU loading).

#### storage

Information of the persistent storage on device.

#### temp

Provides access to temporary files and directories.

#### thermal

System module for thermal control (temperature sensors, fans).

#### touch

Module for touch.

#### toybox

//www.landley.net/toybox/.

* **Type:**
  A python wrapper for http

#### udev

Module for detecting udev event.

#### usb_c

System module for USB type-C.

#### vpd

Interface for read / write Vital Product Data (VPD).

#### vsync_sensor

Camera vertical sync sensors.

#### wifi

Interface for controlling WiFi devices.

### *class* cros.factory.device.device_types.IDeviceLink

An abstract class for connection to remote or local device.

#### *abstractmethod* Push(local: str, remote: str) → None

Uploads a local file to target device.

* **Parameters:**
  * **local** – A string for local file path.
  * **remote** – A string for remote file path on device.

#### *abstractmethod* PushDirectory(local: str, remote: str) → None

Copies a local file to target device.

local should be a local directory, and remote should be a non-existing
file path on device.

Example:

```default
PushDirectory('/path/to/local/dir', '/remote/path/to/some_dir')
```

Will create directory some_dir under /remote/path/to and copy
files and directories under /path/to/local/dir/ to some_dir.

* **Parameters:**
  * **local** – A string for directory path in local.
  * **remote** – A string for directory path on remote device.

#### *abstractmethod* Pull(remote: str, local: None = None) → str | bytes

#### *abstractmethod* Pull(remote: str, local: str) → None

Downloads a file from target device to local.

* **Parameters:**
  * **remote** – A string for file path on remote device.
  * **local** – A string for local file path to receive downloaded content, or
    None to return the contents directly.
* **Returns:**
  If local is None, return bytes or a string as contents in remote file.
  Otherwise, do not return anything.

#### *abstractmethod* PullDirectory(remote: str, local: str) → None

Downloads a directory from target device to local.

#### *abstractmethod* Shell(command: str | Sequence[str], stdin: None | int | IO[Any] = None, stdout: None | int | IO[Any] = None, stderr: None | int | IO[Any] = None, cwd: str | None = None, encoding: str | None = 'utf-8') → Any

Executes a command on device.

The calling convention is similar to subprocess.Popen, but only a subset of
parameters are supported due to platform limitation.

* **Parameters:**
  * **command** – A string or a list of strings for command to execute.
  * **stdin** – A file object to override standard input.
  * **stdout** – A file object to override standard output.
  * **stderr** – A file object to override standard error.
  * **cwd** – The working directory for the command.
  * **encoding** – Same as subprocess.Popen, we will use utf-8 as default to make
    it output str type.
* **Returns:**
  An object representing the process, similar to subprocess.Popen.

#### *abstractmethod* IsReady() → bool

Checks if device is ready for connection.

* **Returns:**
  A boolean indicating if target device is ready.

#### *abstractmethod* IsLocal() → bool

Checks if the target device exactly the local machine.

This is helpful for tests to decide if they can use Python native modules or
need to invoke system commands.

* **Returns:**
  True if the target device is local; False if remote or not certain.

#### *classmethod* PrepareLink() → None

Setup prerequisites of device connections.

Some device types need to do some setup before we can connect to.
For example, we might need to start a DHCP server that assigns IP addresses
to devices.
