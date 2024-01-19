# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Types related to probing.

The types here are shared by RuntimeProbe / ProbeInfoService and HWID Service.
They could be mapped / converted to corresponding protobuf types in each
components above.

TODO(b/321187067): Remove probe_config_types.py after fully migrated types to
this file.
TODO(b/307677458): Evaluate the possibility to integreate this to protobuf
types. We might generate these type automatically or just use the protobuf
binding. Note that currently protobuf bindings don't work well with type hints.
"""

import enum
from typing import Collection, Mapping, NamedTuple


class ProbeFunctionIdentifier(enum.Enum):
  """Identifiers for pre-defined probe function + matchers combinations.

  The ProbeInfo use this to specify how to probe and to match a component. Each
  can be mapped to a probe function with arguments and a matcher to match the
  component by the ProbeInfo.
  """
  USB_CAMERA = 1
  MIPI_CAMERA = 2


class ProbeFunction(NamedTuple):
  """Describes a RuntimeProbe ProbeFunction."""
  name: str
  args: Mapping[str, str]


class ExpectedField(NamedTuple):
  """A expected field of a component."""
  field_name: str
  value: str


class ProbeInfo(NamedTuple):
  """Contains all information to probe a specific component.

  expected_fields: List of all possible values of fields, grouped by field
                   names.
  """
  component_name: str
  probe_function_identifier: ProbeFunctionIdentifier
  expected_fields: Mapping[str, Collection[ExpectedField]]


class MatherOperator(enum.Enum):
  """Matcher operators which are supported in RuntimeProbe.

  Only these can be used in the probe config. Should be implemented in
  RuntimeProbe before adding it.
  """
  AND = 1
  OR = 2
  STRING_EQUAL = 3
  HEX_EQUAL = 4
  INTEGER_EQUAL = 5
  RE = 6


class Component(NamedTuple):
  """Describes a (hardware) component.

  This should be something probed by RuntimeProbe or stored in HWID DB.
  """
  name: str
  field_values: Mapping[str, str]
