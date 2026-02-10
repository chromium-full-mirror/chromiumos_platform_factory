# Test List API

## Overview

The Test List API is used to create test lists.  A test list
is a specification for the series of tests that should be run as part
of the factory test process, and in what order and under what
conditions.

Each test list is a tree of nodes.  Conceptually, each node is one of
the following:

* A container for other tests (like a folder in the filesystem).  When
  a container is run, the tests that it contains are run in sequence.
* A pytest, which is a test written using the standard Python unit test API.

Each test lists has an ID (like `main` or `manual_smt`) that
describes what the test list does.  There is always a test list with
ID `main`; the active test list defaults to `main` but this can be
changed in various ways (see [The active test list](#active-test-list)).

<a id="active-test-list"></a>

## The active test list

The file `/usr/local/factory/py/config/active_test_list.json` is used to
determine which test list is currently active.  This file contains the ID of
the active test list.  If this file is not present, then there are two ways to
determine the default test list;

* ID - `main_${model}` would be checked first where `${model}` is came from
  output of command - `cros_config / name`.
* the test list with ID - `main` or `generic_main` is used.

If you want a different test list to be included by default, you
may simply add an argument `--default-test-list <test-list-id>` to the
factory toolkit installer while installing it to either a test image or a
device.

In engineering mode in the test UI, the operator may select Select
test list from the main menu.  This will display all
available test lists.  Selecting one will clear all test state,
write the ID of the selected test list to the `active_test_list.json` file,
and restart the test harness.

<a id="test-paths"></a>

## Test IDs and paths

Within a test list, each node has an ID (like `LTEModem` or
`CalibrateTouchScreen`).  IDs do not have to be unique across the
entire test list, but they must be unique among all nodes that share
a parent.

To uniquely identify a node within a test list, each node has a
path that is constructed by starting at the root and
concatenating all the node’s IDs with periods.  Conceptually this is
very similar to how paths are formed in a UNIX file system (except
that UNIX file systems use slashes instead of periods) or in a Java
class hierarchy.  For example, if the `LTEModem` test in is a test
group called `Connectivity`, then its path would be
`Connectivity.LTEModem`.

The “root node” is a special node that contains the top-level nodes
in the test list.  Its path is the empty string `''`.

For instance, in [Test list creation sample](#test-list-creation-sample), the `main`
test list contains nodes with the following paths:

* `''` (the root node)
* `FirstTest`
* `SecondTest`
* `ATestGroup`
* `ATestGroup.FirstTest`
* `ATestGroup.SecondTest`

Logs and error messages generally contain the full path when referring
to a test, so you can easily identify which test the message is
referring to.

<a id="declaring-test-lists"></a>

## Declaring test lists

Each test list should be defined by a JSON file with file name
`<test_list_id>.test_list.json` under `py/test/test_lists/` directory.  The
generic test list is defined by
`py/test/test_lists/generic_main.test_list.json`.

In general, when you start working on your own test list, you need to define
two test list files, `common.test_list.json` and `main.test_list.json`.

`common.test_list.json`:

```default
{
  "inherit": [
    "generic_common.test_list"
  ],
  "constants": {
    # Common constants for your project.
  },
  "options": {
    # Common test list options for your project.
  },
  "definitions": {
    # Define new pytests, or override pytest arguments.
  }
}
```

`main.test_list.json`:

```default
{
  "inherit": [
    "common.test_list",
    "generic_main.test_list"
  ],
  "constants": {
    # Constants for this test list.
  }
  "options": {
    # Options for this test list.
  },
  "definitions": {
    "FATItems": [
      # Redefine FATItems (adding, removing, reordering)
    ],
    ...
  }
}
```

<a id="test-list-creation-sample"></a>

## Test list creation sample

Board specific test lists should be placed in board overlay
(`src/private-overlays/overlay-*board*-private/chromeos-base/factory-board/files/py/test/test_lists/`).
And they should reuse test lists in public repository (i.e.
`generic_*.test_list.json`).

For example `common.test_list.json`:

```default
{
  "inherit": [
    "generic_common.test_list"
  ],
  "constants": {
    "allow_force_finalize": [],  # Not allowed.
    "enable_factory_server": true,
    "led_colors": [
      "WHITE",
      "AMBER",
      "OFF"
    ],
    "lid_switch_event_id": 1,
    "light_sensor_input": "in_illuminance_input",
    "min_release_image_version": "9777.0",
    "sysfs_path_sd": "/sys/devices/pci0000:00/0000:00:1e.6/mmc_host/",
    "typec_usb": {
      "left": {
        "usb2_sysfs_path": "/sys/devices/pci0000:00/0000:00:14.0/usb1/1-1",
        "usb3_sysfs_path": "/sys/devices/pci0000:00/0000:00:14.0/usb2/2-1",
        "usbpd_id": 0,
        "display_info": [
          "DisplayPort",
          "DP-1"
        ]
      },
      "right": {
        "usb2_sysfs_path": "/sys/devices/pci0000:00/0000:00:14.0/usb1/1-5",
        "usb3_sysfs_path": "/sys/devices/pci0000:00/0000:00:14.0/usb2/2-2",
        "usbpd_id": 1,
        "display_info": [
          "DisplayPort",
          "DP-2"
        ]
      }
    }
  }
}
```

Sample `main.test_list.json`:

```default
{
  "inherit": [
    "common.test_list",
    "generic_main.test_list"
  ],
  "constants": {
    "default_factory_server_url": "http://192.168.111.222:8888/"
  },
  "options": {
    "conditional_patches": [
      {
        "action": "skip",
        "conditions": {
          "patterns": [
            "*.AudioJack",
            "*.SpeakerDMic"
          ],
          "phases": "PROTO"
        }
      }
    ]
  }
}
```

Note the following crucial parts:

* `options` is a dictionary that defines test list options, as described in
  [Test list options](#test-list-options).

## Test arguments

It is often necessary to customize the behavior of various tests, such
as specifying the amount of time that a test should run, or which device
it should use.  For this reason, tests can accept arguments that modify
their functionality.

Most pytests should already be defined by `generic_common`, you only need to
override test arguments.  For example, in your `common.test_list.json`:

```default
{
  ...,
  "definitions": {
    "QRScan": {
      "args": {
        # Only override "camera_args".
        "camera_args": {
          "resolution": [
            1280,
            720
          ]
        }
      }
    }
  }
}
```

In this case, test arguments for QRScan will be:

```default
{
  # defined by generic_common.test_list.json
  "mode": "qr",
  "QR_string": "Hello ChromeOS!",
  # defined by common.test_list.json
  "camera_args": {
    "resolution": [
      1280,
      720
    ]
  }
}
```

If you want to **replace** `args` completely, instead of updating, you should
use `__replace__` keyword:

```default
{
  ...,
  "definitions": {
    "QRScan": {
      "args": {
        "__replace__": true,
        # definitions in generic_common will be disgarded
        ...
      }
    }
  }
}
```

A description of the permissible arguments for each test, and their
defaults, is included in the `ARGS` property in the class that
implements the test.

<a id="test-list-options"></a>

## Test list options

### *class* cros.factory.test.test_lists.test_list.Options

Test list options.

These may be set by assigning to the options variable in a test list,
e.g.:

```default
test_list.options.auto_run_on_start = False
```

#### auto_run_on_start *= True*

If set to True, then the test list is automatically started when
the test harness starts.  If False, then the operator will have to
manually start a test.

#### retry_failed_on_start *= False*

If set to True, then the failed tests are automatically retried
when the test harness starts. It is effective when auto_run_on_start
is set to True.

#### clear_state_on_start *= False*

If set to True, the state of all tests is cleared each time the
test harness starts.

#### auto_run_on_keypress *= False*

If set to True, the test harness will perform an auto-run whenever
the operator switches to any test.

#### ui_locale *= 'en-US'*

The default UI locale.

#### engineering_password_sha1 *= None*

SHA1 hash for a engineering password in the UI.  Use None to
always enable engingeering mode.

To enter engineering mode, an operator may press Ctrl-Alt-0 and
enter this password.  Certain special functions in the UI (such as
being able to arbitrarily run any test) will be enabled.  Pressing
Ctrl-Alt-0 will exit engineering mode.

In order to keep the password hidden from operator (even if they
happen to see the test list file), the actual password is not stored
in the test list; rather, a hash is.  To generate the hash, run:

```default
echo -n password | sha1sum
```

For example, for a password of `test0000`, run:

```default
echo -n test0000 | sha1sum
```

This will display a hash of `266abb9bec3aff5c37bd025463ee5c14ac18bfca`,
so you should set:

```default
test.list.options.engineering_password_sha1 =         '266abb9bec3aff5c37bd025463ee5c14ac18bfca'
```

#### sync_event_log_period_secs *= None*

Send events to the factory server when it is reachable at this
interval.  Set to `None` to disable.

#### update_period_secs *= None*

Automatically check for updates at the given interval.  Set to
`None` to disable.

#### stop_on_failure *= False*

Whether to stop on any failure.

#### hooks_class *= 'cros.factory.goofy.hooks.Hooks'*

Hooks class for the factory test harness.  Defaults to a dummy class.

#### testlog_hooks *= 'cros.factory.testlog.hooks.Hooks'*

Hooks class for Testlog event. Defaults to a dummy class.

#### phase *= None*

Name of a phase to set.  If None, the phase is unset and the
strictest (PVT) checks are applied.

#### dut_options *= {}*

Options for DUT target.  Automatically inherits from parent node.
Valid options include:

```default
{'link_class': 'LocalLink'},  # To run tests locally.
{'link_class': 'ADBLink'},  # To run tests via ADB.
{'link_class': 'SSHLink', 'host': TARGET_IP},  # To run tests over SSH.
```

See [`cros.factory.device.device_utils`](device_api.md#module-cros.factory.device.device_utils) for more information.

#### plugin_config_name *= 'goofy_plugin_chromeos'*

Name of the config to be loaded for running Goofy plugins.

#### read_device_data_from_vpd_on_init *= True*

Read device data from VPD in goofy._InitStates().

#### skipped_tests *= {}*

A list of tests that should be skipped.
The content of `skipped_tests` should be:

```default
{
  "<phase>": [ <pattern> ... ],
  "<run_if expr>": [ <pattern> ... ]
}
```

For example:

```default
{
  "PROTO": [
    "SMT.AudioJack",
    "SMT.SpeakerDMic",
    "*.Fingerprint"
  ],
  "EVT": [
    "SMT.AudioJack",
  ],
  "not device.component.has_touchscreen": [
    "*.Touchscreen"
  ],
  "device.factory.end_SMT": [
    "SMT"
  ]
}
```

If the pattern starts with `*`, then it will match for all tests with same
suffix.  For example, `*.Fingerprint` matches `SMT.Fingerprint`,
`FATP.FingerPrint`, `FOO.BAR.Fingerprint`.  But it does not match for
`SMT.Fingerprint_2` (Generated ID when there are duplicate IDs).

#### waived_tests *= {}*

Tests that should be waived according to current phase.
See `skipped_tests` for the format

#### conditional_patches *= []*

A list contains patches to apply to the tests.

The action of each patch will be applied to all the test meeting the specified
conditions.

The structure of the patch list must be like:

```default
[
  {
    "action": "waive" | "skip",
    "args": { ... },
    "conditions": {
      "run_if": "<run_if expr>" | [ "<run_if expr>", ... ],
      "patterns": "<pattern>" | [ "<pattern>", ... ],
      "phases": "<phase>" | [ "<phase>", ... ],
    }
  },
  ...
]
```

For example:

```default
[
  {
    "action": "skip",
    "conditions": {
      "run_if": "not device.component.has_touchscreen",
      "patterns": "*.Touchscreen"
    }
  },
  {
    "action": "skip",
    "conditions": {
      "patterns": [
        "SMT.AudioJack",
        "SMT.SpeakerDMic",
        "*.Fingerprint",
      ],
      "phases": ["PROTO", "EVT"],
    }
  },
  {
    "action": "skip",
    "conditions": {
      "patterns": "SMT.AudioJack",
      "phases": "EVT",
    }
  }
]
```

Usage of each field:

* **action**: The action to be applied to the tests.

  action is a string representing the action applied to the tests which meet
  the conditions. An action will be mapped to a action function.
* **args**: Keyword arguments to be passed to action functions.

  args is an object containing keyword arguments which will be passed to the
  action functions.
* **conditions**:
  * **patterns** (*required*): The patterns used to match the test list paths.

    If a pattern starts with `*`, then it will match for all tests with
    same suffix. For example, `*.Fingerprint` matches `SMT.Fingerprint`,
    `FATP.FingerPrint`, `FOO.BAR.Fingerprint`. But it does not match for
    `SMT.Fingerprint_2` (Generated ID when there are duplicate IDs). On the
    other hand, `*` can also be put at the end of a pattern, then it will
    match for all tests with the same prefix.

    `*` can be put at both the beginning and the end of a pattern (e.g.
    `*.Fingerprint.*`), but not within a pattern.

    For single-pattern cases (only having one pattern to be matched), one can
    set the value of patterns as the pattern directly (without wrapping it
    as an array) for convenience.

    For multiple-pattern cases, the patterns included will be treated as a
    disjuction, that is, a test will pass patterns condition if it matches
    any one of the patterns.
  * **phases** (*optional*): The phases that will apply the patch.

    If phases is not set or it’s empty, the patch will be applied to all
    phases (other condition like patterns still need to be checked).

    For single-phase cases (only having one phase to be included), one can set
    the value of phases as the phase directly.

    For multiple-phase cases, the phases included will be treated as a
    disjuction, that is, a test will pass phases condition if the DUT is on
    any one of the phases.
  * **run_if** (*optional*): A set of run_if expressions.

    The expressions in the array are to be evaluated and checked. Please check
    `AbstractTestList._EvaluateRunIf` to see how an expression is evaluated.

    If run_if is not set or it’s empty, this field will be ignore and check
    other fields only.

    For single-run_if cases (only having one run_if expre to be evaluated),
    one can set the value of run_if as the run_if directly.

    For multiple-phase cases, the run_if included will be treated as a
    disjuction, that is, a test will pass run_if condition if any one of the
    expressions is evaluated as True.

#### CheckValid()

Throws a TestListError if there are any invalid options.

#### ToDict()

Returns a dict containing all values of the Options.

This include default values for keys not set on the Options.
