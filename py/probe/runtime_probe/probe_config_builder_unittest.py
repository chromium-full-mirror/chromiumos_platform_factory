#!/usr/bin/env python3
# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import textwrap
import unittest

from cros.factory.probe.runtime_probe import matchers
from cros.factory.probe.runtime_probe import probe_config_builder


class ProbeConfigBuilderTest(unittest.TestCase):

  def testBuild(self):
    builder = probe_config_builder.ProbeConfigBuilder()
    builder.AddComponent('category_a', 'component_a', 'probe_function_a', {
        'arg1': 'value_1'
    })
    builder.AddComponent('category_a', 'component_b', 'probe_function_a', {
        'arg1': 'value_1'
    }, matchers.StringEqualMatcher('field_a', 'value_a'))

    self.assertEqual(
        textwrap.dedent("""\
            {
              "category_a": {
                "component_a": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  }
                },
                "component_b": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  },
                  "matcher": {
                    "operand": [
                      "field_a",
                      "value_a"
                    ],
                    "operator": "STRING_EQUAL"
                  }
                }
              }
            }
            """), builder.Build())

  def testLegacyBuild(self):
    builder = probe_config_builder.ProbeConfigBuilder(
        textwrap.dedent("""\
            {
              "category_a": {
                "component_c": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  },
                  "expect": {
                    "field_a": [
                      true,
                      "str",
                      "!eq value_a"
                    ]
                  }
                }
              }
            }
            """))
    builder.AddComponent('category_a', 'component_a', 'probe_function_a', {
        'arg1': 'value_1'
    })
    builder.AddComponent('category_a', 'component_b', 'probe_function_a', {
        'arg1': 'value_1'
    }, matchers.StringEqualMatcher('field_a', 'value_a'))
    self.assertEqual(
        textwrap.dedent("""\
            {
              "category_a": {
                "component_a": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  }
                },
                "component_b": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  },
                  "matcher": {
                    "operand": [
                      "field_a",
                      "value_a"
                    ],
                    "operator": "STRING_EQUAL"
                  }
                },
                "component_c": {
                  "eval": {
                    "probe_function_a": {
                      "arg1": "value_1"
                    }
                  },
                  "expect": {
                    "field_a": [
                      true,
                      "str",
                      "!eq value_a"
                    ]
                  }
                }
              }
            }
            """), builder.Build())


if __name__ == '__main__':
  unittest.main()
