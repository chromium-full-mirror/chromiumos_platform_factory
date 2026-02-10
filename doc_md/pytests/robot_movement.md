# robot_movement

**Source code:** [robot_movement.py](https://chromium.googlesource.com/chromiumos/platform/factory/+/refs/heads/main/py/test/pytests/robot_movement.py)

Control a robot to move a device for testing specific sensors.

## Description

This test controls a robot (arm) to move a device along a predefined
trajectory, to verify the functionalities of the sensors on the device.

## Test Procedure

1. Robot is moved to the unloaded position.
2. Ask the operator to mount the device.
3. Robot is moved to the loaded position.
4. Robot is moved by the given trajectory.
5. Robot is moved to the unloaded position.
6. Verify the data from sensors on the device.
7. Ask the operator to unmount the device.

## Dependency

Depend on the class specified by the arguments robot_fixture and
algorithm to move the robot, get result from the device, and
verify the result.

## Examples

To use robot.foo to control the robot fixture, and use algo.bar to
calculate and verify the sensor data, add this in test list:

```default
{
  "pytest_name": "robot_movement",
  "args": {
    "positions": [0, 1, 2, 3, 4, 5],
    "robot_fixture": "robot.foo",
    "algorithm": "algo.bar"
  }
}
```

One can also pass parameters to the classes specified in robot_fixture and
algorithm:

```default
{
  "pytest_name": "robot_movement",
  "args": {
    "positions": [0, 1, 2, 3, 4, 5],
    "robot_fixture": "robot.foo",
    "robot_fixture_args": {
      "speed": 30
    },
    "algorithm_args": {
      "trajectory_id": "bar1"
    },
    "algorithm": "algo.bar"
  }
}
```

## Test Arguments

| Name                    | Type       | Description                                                                                                                                                                                           |
|-------------------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| robot_fixture           | str        | The class name of the robot fixture under `cros.factory.test.fixture`, should be a subclass of `cros.factory.test.fixture.imu.robot.Robot`.E.g. robot.dummy_robot.DummyRobot                          |
| robot_fixture_args      | dict       | (optional; default: `{}`) A dict of the args used for the constructor of the robot_fixture.                                                                                                           |
| algorithm               | str        | The class name of the computing method under `cros.factory.test.fixture`, should be a subclass of `cros.factory.test.fixture.robot.algorithm.BaseAlgorithm`.E.g. robot.dummy_algorithm.DummyAlgorithm |
| algorithm_args          | dict       | (optional; default: `{}`) A dict of the args used for the constructor of the algorithm.                                                                                                               |
| period_between_movement | float, int | (optional; default: `0.5`) The pause period between two movements.                                                                                                                                    |
| period_after_movement   | float, int | (optional; default: `0.0`) The pause period after the final movements.                                                                                                                                |
| positions               | list       | A list of position index for the robot to move.                                                                                                                                                       |
| upload_to_server        | bool       | (optional; default: `False`) If true, upload log to factory server after running.                                                                                                                     |
