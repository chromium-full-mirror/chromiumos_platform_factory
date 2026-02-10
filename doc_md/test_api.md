# Test API

## Overview

This document describes how to write new factory tests and integrate
them into the testing framework.

## Basics

Factory tests are implemented as Python unit tests. Each factory test
is a subclass of the [unittest.TestCase](https://docs.python.org/2/library/unittest.html#unittest.TestCase)
class, and may make full use of the Python `unittest` API (e.g., all
the `assert` methods, `fail`, `setUp`, `tearDown`, etc.). The
factory SDK also provides APIs that can be used to parse test
arguments (see [Test arguments]()), and to interact with the test UI
running in the browser (see [Test UI API](test_ui_api.md#test-ui-api)).

Each factory test should at minimum contain

* a `runTest` method
  containing the test implementation (see [Test implementation]()), and
* an `ARGS` attribute describing the arguments that may be used
  by the test list when invoking the test (see [Test arguments]()).

## Where to put your test

Each factory has a name (like `bad_blocks` or `lcd_backlight`).
For simple tests containing only a Python file, put the test code
in

> `py/test/pytests/*name*.py`

Alternatively, if your test has accompanying files (such as HTML or
JavaScript files), you may create a directory for it and put the code
in

> `py/test/pytests/*name*/*name*.py`. <sup>[\*](#id2)</sup>

Within this file, there should be a single subclass of unittest.TestCase.
There can be only one test class per module, so if you need to have different
test cases, you need to separate them into different modules. But you can create
a directory for them, for example:

> - `py/test/pytests/*dir_name*/*test1*.py`
> - `py/test/pytests/*dir_name*/*test2*.py`
> - `py/test/pytests/*dir_name*/*test3*.py`.

In this case, the name of your tests are `*dir_name*.*test1*`,
`*dir_name*.*test2*` and `*dir_name*.*test3*`.

To know more about how we load a pytest from name, please refer to
[`cros.factory.test.utils.pytest_utils.LoadPytestModule()`](#cros.factory.test.utils.pytest_utils.LoadPytestModule).

* <a id='id2'>**[\*]**</a> Since the `__init__.py` of a package will be loaded whenever its submodule is imported. We recommand keeping `__init__.py` empty to prevent longer loading time if `__init__.py` is too large.

## Test implementation

Your test should contain a `runTest` method containing the body of
the test.  (As with all Python unittests, it may also contain a
`setUp` and `tearDown` method.  `setUp` is run first, and
`tearDown` is run after the test passes or fails; although note
that `tearDown` may not be run if the test is forcibly stopped.)

The test is considered to have succeeded if the `runTest` method
returns.  The test will fail if:

* your test calls any of the `unittest.TestCase.assertXXX` methods,
  such as [assertTrue](https://docs.python.org/2/library/unittest.html#unittest.TestCase.assertTrue),
  and the assertion fails. For example, this will cause your test to
  fail with a good error message if a file does not exist as expected:
  > self.assertTrue(
  > : os.path.exists(self.args.path),
  >   ‘File %r does not exist’ % self.args.path)
* your test calls self.fail
  <https://docs.python.org/2/library/unittest.html#unittest.TestCase.fail>,
  which tells the Python unit test framework to raise an exception.
* your test directly raises an exception with `raise`.
* code that you call directly or indirectly raises an exception. For
  example, if you call `subprocess.check_call`, and `check_call`
  raises a `CalledProcessError` that you do not catch, your test
  will fail. If you want such a failure in `check_call` to cause
  your test to fail, you can choose to not catch the exception and let
  it propagate out of your `runTest` method.

There are several key APIs you will need to understand to write your
test:

* [Test arguments]() allow your test to handle arguments specified
  in test lists.
* [Test UI API](test_ui_api.md#test-ui-api) allows your test to provide a UI to interact with
  the operator or show status messages.  If your test is simple and
  does not require interaction with the user, you may choose not to
  provide a UI.

## Test arguments

Test lists need to customize the behavior of tests in various
situations, e.g., to specify different limits or parameters or to
enable/disable various checks. To allow this sort of customization,
you can declare test arguments in your test case by adding an `ARGS`
attribute describing the supported set of arguments. `ARGS` is a
list of items of type [`cros.factory.utils.arg_utils.Arg`](#cros.factory.utils.arg_utils.Arg).

For example:

```default
import unittest
from cros.factory.utils.arg_utils import Arg

class BadBlocksTest(unittest.TestCase):
  ARGS = [
    Arg('path', str, 'The path to a temporary file to use for testing.'),
    Arg('max_bytes', int, 'Maximum size to test, in bytes.',
        default=16*1024*1024),
  ]
```

This declares two arguments: `path` is a required string, and
`max_bytes` is an optional number defaulting to 16 megabytes.

The test list might contain an entry like:

```default
{
  "pytest_name": "bad_blocks",
  "args": {
    "path": "/usr/local/foo",
    "max_bytes": 8388608
  }
}
```

The factory test runner will check that:

* all the arguments in the test list are valid arguments (e.g.,
  you don’t accidentally specify a `filename` argument, since
  `filename` is not declared in `ARGS`).
* all required arguments (in this case `path`) are specified.
* all the arguments are of the correct type (e.g., you don’t say
  `max_bytes='foo'`, since `max_bytes` must be an `int`).

<a id="module-cros.factory.utils.arg_utils"></a>

### *class* cros.factory.utils.arg_utils.Arg(name, type, help, default=<object object>, \_transform=None, schema=None)

The specification for a single test argument.

#### \_\_init_\_(name, type, help, default=<object object>, \_transform=None, schema=None)

Constructs a test argument.

* **Parameters:**
  * **name** – Name of the argument. This will be the key in a `dargs`
    dict in the test list.
  * **type** – 

    Type of the argument, or (if more than one type is permitted)
    a tuple of allowable types. If `default` is None, then None
    is also implicitly allowed. For example:
    ```default
    type=int         # Allow only integers
    type=(int, str)  # Allow int or string
    ```

    You can use `enum.Enum` object as a type:
    ```default
    class EnumTyped(str, enum.Enum):
      a = 'a'
      b = 'b'

      def __str__(self):
      return self.name

    type=EnumTyped
        # Allows only the members in EnumTyped and str 'a' or 'b'.
    ```

    Besides, you can use `enum.Enum` functional API:
    ```default
    type=enum.Enum('enum_obj', 'a b')
    ```

    It also supports `enum.IntEnum` object:
    ```default
    class IntEnumTyped(enum.IntEnum):
      num_1 = 1
      num_2 = 2

    type=IntEnumTyped
        # Allows only the members in IntEnumTyped and int 1 or 2.
    ```
  * **help** – A string describing how to use the argument. This will be
    included in the test catalog in the documentation bundle and
    may be formatted using [reStructuredText](http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html).
  * **default** – A default value for the argument. If there is no
    default value, this is omitted.
  * **\_transform** – A transform function to be applied to the value after the
    argument is resolved.
  * **schema** – A utils.schema object for checking the argument.

Once you have declared the arguments used by your test,
you can use `self.args` anywhere in your test implementation
to refer to the value of that argument.  For example:

```default
class BadBlocksTest(unittest.TestCase)::
  ...  # see above for ARGS = [...] declaration

  def runTest(self):
    logging.info('path=%s, max_bytes=%d',
                 self.args.path, self.args.max_bytes)
```

<a id="module-cros.factory.test.utils.pytest_utils"></a>

### cros.factory.test.utils.pytest_utils.LoadPytestModule(pytest_name)

Loads the given pytest module.

This function tries to load the module

> `cros.factory.test.pytests.*pytest_name*`.
* **Parameters:**
  **pytest_name** – The name of the pytest module.
* **Returns:**
  The loaded pytest module object.
