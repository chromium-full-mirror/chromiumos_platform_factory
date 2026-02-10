# tablet_rotation

**Source code:** [tablet_rotation.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/tablet_rotation.py)

Tests screen rotation through ChromeOS and accelerometer data.

## Description

Tests that the accelerometer data matches the orientation when the device is
physically rotated.

## Test Procedure

1. A picture would be shown on the screen. Operator should rotate the tablet to
   align with the image. This would repeat four times with each orientations,
   and the test automatically pass when the desired orientation is reached.

## Dependency

`chrome.display.system.getInfo` in Chrome extension to get screen
information. Refer to [https://developer.chrome.com/apps/system_display](https://developer.chrome.com/apps/system_display) for
more information.

`cros.factory.device.accelerometer` is used to determine device orientation.

## Examples

To test screen rotation, and have a timeout of an hour:

```default
{
  "pytest_name": "tablet_rotation",
  "label": "Tablet Rotation",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "spec_offset": [
      1.5,
      1.5
    ],
    "timeout_secs": 3600
  }
}
```

To provide more parameters for accelerometer when testing:

```default
{
  "pytest_name": "tablet_rotation",
  "label": "Tablet Rotation Accelerometers",
  "run_if": "not constants.has_device_data or (device.component.has_base_accelerometer and device.component.has_lid_accelerometer)",
  "related_components": [
    "test_tags.TestCategory.ACCELEROMETER"
  ],
  "args": {
    "spec_offset": [
      1.5,
      1.5
    ],
    "timeout_secs": 3600,
    "degrees_to_orientations": {
      "base": {
        "0": {
          "in_accel_x": 0,
          "in_accel_y": -1,
          "in_accel_z": 0
        },
        "90": {
          "in_accel_x": 1,
          "in_accel_y": 0,
          "in_accel_z": 0
        },
        "180": {
          "in_accel_x": 0,
          "in_accel_y": 1,
          "in_accel_z": 0
        },
        "270": {
          "in_accel_x": -1,
          "in_accel_y": 0,
          "in_accel_z": 0
        }
      },
      "lid": {
        "0": {
          "in_accel_x": 0,
          "in_accel_y": 1,
          "in_accel_z": 0
        },
        "90": {
          "in_accel_x": 1,
          "in_accel_y": 0,
          "in_accel_z": 0
        },
        "180": {
          "in_accel_x": 0,
          "in_accel_y": -1,
          "in_accel_z": 0
        },
        "270": {
          "in_accel_x": -1,
          "in_accel_y": 0,
          "in_accel_z": 0
        }
      }
    }
  }
}
```

To test screen rotation for Chrome and prompt operator to flip before and after
the test, we can combine the test with [tablet_mode.py](./tablet_mode.html):

```default
{
  "label": "Screen Rotation",
  "run_if": "not constants.has_device_data or device.component.has_tabletmode",
  "subtests": [
    {
      "pytest_name": "tablet_mode",
      "label": "Tablet Mode",
      "run_if": "not constants.has_device_data or device.component.has_tabletmode",
      "args": {
        "timeout_secs": 3600,
        "prompt_flip_tablet": true,
        "prompt_flip_notebook": false,
        "lid_filter": "cros_ec_buttons"
      }
    },
    {
      "pytest_name": "tablet_rotation",
      "label": "Tablet Rotation Accelerometers",
      "run_if": "not constants.has_device_data or (device.component.has_base_accelerometer and device.component.has_lid_accelerometer)",
      "related_components": [
        "test_tags.TestCategory.ACCELEROMETER"
      ],
      "args": {
        "spec_offset": [
          1.5,
          1.5
        ],
        "timeout_secs": 3600,
        "degrees_to_orientations": {
          "base": {
            "0": {
              "in_accel_x": 0,
              "in_accel_y": -1,
              "in_accel_z": 0
            },
            "90": {
              "in_accel_x": 1,
              "in_accel_y": 0,
              "in_accel_z": 0
            },
            "180": {
              "in_accel_x": 0,
              "in_accel_y": 1,
              "in_accel_z": 0
            },
            "270": {
              "in_accel_x": -1,
              "in_accel_y": 0,
              "in_accel_z": 0
            }
          },
          "lid": {
            "0": {
              "in_accel_x": 0,
              "in_accel_y": 1,
              "in_accel_z": 0
            },
            "90": {
              "in_accel_x": 1,
              "in_accel_y": 0,
              "in_accel_z": 0
            },
            "180": {
              "in_accel_x": 0,
              "in_accel_y": -1,
              "in_accel_z": 0
            },
            "270": {
              "in_accel_x": -1,
              "in_accel_y": 0,
              "in_accel_z": 0
            }
          }
        }
      }
    },
    {
      "pytest_name": "tablet_rotation",
      "label": "Tablet Rotation Base-Accel",
      "run_if": "constants.has_device_data and device.component.has_base_accelerometer",
      "related_components": [
        "test_tags.TestCategory.ACCELEROMETER"
      ],
      "args": {
        "spec_offset": [
          1.5,
          1.5
        ],
        "timeout_secs": 3600,
        "degrees_to_orientations": {
          "base": {
            "0": {
              "in_accel_x": 0,
              "in_accel_y": -1,
              "in_accel_z": 0
            },
            "90": {
              "in_accel_x": 1,
              "in_accel_y": 0,
              "in_accel_z": 0
            },
            "180": {
              "in_accel_x": 0,
              "in_accel_y": 1,
              "in_accel_z": 0
            },
            "270": {
              "in_accel_x": -1,
              "in_accel_y": 0,
              "in_accel_z": 0
            }
          }
        }
      }
    },
    {
      "pytest_name": "tablet_rotation",
      "label": "Tablet Rotation Lid-Accel",
      "run_if": "constants.has_device_data and device.component.has_lid_accelerometer",
      "related_components": [
        "test_tags.TestCategory.ACCELEROMETER"
      ],
      "args": {
        "spec_offset": [
          1.5,
          1.5
        ],
        "timeout_secs": 3600,
        "degrees_to_orientations": {
          "lid": {
            "0": {
              "in_accel_x": 0,
              "in_accel_y": 1,
              "in_accel_z": 0
            },
            "90": {
              "in_accel_x": 1,
              "in_accel_y": 0,
              "in_accel_z": 0
            },
            "180": {
              "in_accel_x": 0,
              "in_accel_y": -1,
              "in_accel_z": 0
            },
            "270": {
              "in_accel_x": -1,
              "in_accel_y": 0,
              "in_accel_z": 0
            }
          }
        }
      }
    },
    {
      "pytest_name": "tablet_mode",
      "label": "Notebook Mode",
      "run_if": "not constants.has_device_data or device.component.has_tabletmode",
      "args": {
        "timeout_secs": 3600,
        "prompt_flip_tablet": false,
        "prompt_flip_notebook": true,
        "lid_filter": "cros_ec_buttons"
      }
    }
  ]
}
```

## Test Arguments

| Name                    | Type                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|-------------------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| timeout_secs            | int                      | (optional; default: `30`) Timeout value for the test.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| degrees_to_orientations | dict                     | (optional; default: `{'base': {'0': {'in_accel_x': 0, 'in_accel_y': -1, 'in_accel_z': 0}, '90': {'in_accel_x': 1, 'in_accel_y': 0, 'in_accel_z': 0}, '180': {'in_accel_x': 0, 'in_accel_y': 1, 'in_accel_z': 0}, '270': {'in_accel_x': -1, 'in_accel_y': 0, 'in_accel_z': 0}}, 'lid': {'0': {'in_accel_x': 0, 'in_accel_y': 1, 'in_accel_z': 0}, '90': {'in_accel_x': 1, 'in_accel_y': 0, 'in_accel_z': 0}, '180': {'in_accel_x': 0, 'in_accel_y': -1, 'in_accel_z': 0}, '270': {'in_accel_x': -1, 'in_accel_y': 0, 'in_accel_z': 0}}}`) The keys should be “base” or “lid”, which are the locations of the accelerometer. And each value is a dict of (key, value) pair as follows: Keys: degrees of the orientations, [“0”, “90”, “180”, “270”]. Values: a dictionary containing orientation configuration.  Keys should be the name of the accelerometer signal. The possible keys are “in_accel_(x|y|z)”. Values should be one of [0, 1, -1], representing the ideal value for gravity under such orientation. |
| spec_offset             | list                     | (optional; default: `[1, 1]`) Two numbers, ex: [1.5, 1.5] indicating the tolerance for the digital output of sensors under zero gravity and one gravity.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| sample_rate_hz          | int                      | (optional; default: `200`) The sample rate in Hz to get raw data from accelerometers.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| mode                    | [‘animation’, ‘classic’] | (optional; default: `'classic'`) The mode for showing instruction of the test                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
