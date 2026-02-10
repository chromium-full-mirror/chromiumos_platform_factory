<a id="test-ui-api"></a>

# Test UI API

The Test UI API allows tests to interact with an operator, or to
display their status to the operator while they are running.

To use the test UI, inherit from
`cros.factory.test.test_case.TestCase` instead of
`unittest.TestCase` for the unittest. You can then call various
methods on `self.ui` (which is of type
[`cros.factory.test.test_ui.StandardUI`](#cros.factory.test.test_ui.StandardUI)) to interact with the browser
(see [Test UI Class Reference]()).

For example, this test displays “Hello, world” in the UI, waits
five seconds, and then passes:

```default
import time
from cros.factory.test import test_ui

class MyTest(test_case.TestCase):
  def runTest(self):
    self.template.SetState('Hello, world!')
    self.Sleep(5)
```

The following document assumes that the test inherit from
`cros.factory.test.test_case.TestCase`.

See [Test Internationalization API](test_i18n_api.md#test-i18n-api) on how to display localized texts on UI.

## Including static resources

Often you will want to include static resources, such as images, HTML,
and JavaScript code, in your UI. Where to put static resources
depends on how you have laid out your test directory.

### Simple layout

If your test is called `*mytest*` and your test code is in the
file `py/test/pytests/*mytest*.py`, you may include static
resources in a directory called

> `py/test/pytests/*mytest*_static`

In addition, these files will be automatically loaded if they exist:

* `py/test/pytests/*mytest*_static/*mytest*.html`
* `py/test/pytests/*mytest*_static/*mytest*.js`
* `py/test/pytests/*mytest*_static/*mytest*.css`

### Nested layout

If your test has its own subdirectory (i.e., your test code is in
`py/test/pytests/*mytest*/*mytest*.py`), then you can create a
`static` directory within your test’s subdirectory, and put static
resources there:

> `py/test/pytests/*mytest*/static`

In addition, these files will be automatically loaded if they exist:

* `py/test/pytests/*mytest*/static/*mytest*.html`
* `py/test/pytests/*mytest*/static/*mytest*.js`
* `py/test/pytests/*mytest*/static/*mytest*.css`

### Referring to static resources

Within your UI, you can refer to static resources with relative
paths. For instance, if you have a file called `foo.png` in your
static directory:

> `py/test/pytests/*mytest*/static/foo.png`

You may simply use this HTML to refer to the image:

> `<img src="foo.png">`

Alternatively, you can use an absolute path:

> `<img src="/tests/*mytest*/foo.png">`

## Pass or fail the test

To fail the test, do one of the followings:

* Calls `window.test.fail(msg)` in JavaScript implementation.
* Raises exception in either `runTest` or in the event handlers (Can be
  exception raised by calling various `self.assert*` methods from
  `unittest.TestCase`).
* Calls `self.FailTask(error_msg)`, which is exactly the same as `raise
  type_utils.TestFailure(error_msg)`.

To pass the test, do one of the followings:

* Calls `window.test.pass()` in JavaScript implementation.
* Calls `self.PassTask()` in either `runTest` or in the event handlers.
* If nothing fails the test, the test is **automatically passed after**
  `runTest` **return**. To wait for either pass or fail is explictly called,
  call `self.WaitTaskEnd()` at the end of `runTest`, and the test would
  wait for one of the conditions above is achieved.

When the test inherits from `test_case.TestCase`, the `runTest` method is
run in a **background** thread, while the UI event loop run in the main thread.

The `PassTask`, `FailTask` and raises exception to fail test only works in
either event handlers or in the `runTest` thread. To achieve same behavior on
other threads, wrap the function with `self.event_loop.CatchException`. For
example:

```default
def BackgroundWork(self):
  # Background works that have to be done in another thread.

def runTest(self):
  thread = process_utils.StartDaemonThread(
      target=self.event_loop.CatchException(self.BackgroundWork))
  # Do some other things in parallel with BackgroundWork.
```

## Test UI Templates

There are default templates for test to keep look and feel consistent across
tests. To access the template, use methods on
[`cros.factory.test.test_ui.StandardUI`](#cros.factory.test.test_ui.StandardUI). For example:

```default
class MyTest(test_case.TestCase):
  def runTest(self):
    self.ui.SetTitle('My Test')
    self.ui.SetState('Hello, world!')
    ...
```

To change what UI class is used for `self.ui`, set the `ui_class` for the
test class. For example:

```default
class MyTest(test_case.TestCase):
  ui_class = test_ui.ScrollableLogUI

  def runTest(self):
    self.ui.AppendLog('some log')
```

## Test UI Class Reference

### *class* cros.factory.test.test_ui.UI(event_loop)

Web UI for a factory test.

#### SetHTML(html, id, append=False, autoscroll=False)

Sets a HTML snippet to the UI in the test pane.

Note that <script> tags are not allowed in SetHTML() and
AppendHTML(), since the scripts will not be executed. Use RunJS()
or CallJSFunction() instead.

* **Parameters:**
  * **html** – The HTML snippet to set.
  * **id** – Writes html to the element identified by id.
  * **append** – Whether to append the HTML snippet.
  * **autoscroll** – If True and the element scroll were at bottom before SetHTML,
    scroll the element to bottom after SetHTML.

#### AppendHTML(html, \*\*kwargs)

Append to the UI in the test pane.

#### AppendCSS(css)

Append CSS in the test pane.

#### AppendCSSLink(css_link)

Append CSS link in the test pane.

#### RunJS(js, \*\*kwargs)

Runs JavaScript code in the UI.

* **Parameters:**
  * **js** – The JavaScript code to execute.
  * **kwargs** – Arguments to pass to the code; they will be
    available in an “args” dict within the evaluation
    context.

### Example

ui.RunJS(‘alert(args.msg)’, msg=’The British are coming’)

#### CallJSFunction(name, \*args)

Calls a JavaScript function in the test pane.

This is implemented by calling to RunJS, so the ‘this’ variable in
JavaScript function would be ‘correct’.

For example, calling CallJSFunction(‘test.alert’, ‘123’) is same as calling
RunJS(‘test.alert(args.arg_0)’, arg_0=’123’), and the ‘this’ when the
‘test.alert’ function is running would be test instead of window.

* **Parameters:**
  * **name** – The name of the function to execute.
  * **args** – Arguments to the function.

#### InitJSTestObject(class_name, \*args)

Initialize a JavaScript test object in frontend.

The JavaScript object would be at window.testObject.

* **Parameters:**
  * **class_name** – The class name of the JavaScript test object.
  * **args** – Argument passed to the class constructor.
* **Returns:**
  A JavaScriptProxy to the frontend test object.

#### URLForFile(path)

Returns a URL that can be used to serve a local file.

* **Parameters:**
  **path** – path to the local file
* **Returns:**
  A (possibly relative) URL that refers to the file
* **Return type:**
  url

#### GetStaticDirectoryPath()

Gets static directory os path.

* **Returns:**
  OS path for static directory; Return None if no static directory.

#### BindStandardPassKeys()

Binds standard pass keys (enter, space, ‘P’).

#### BindStandardFailKeys()

Binds standard fail keys (ESC, ‘F’).

#### BindStandardKeys()

Binds standard pass and fail keys.

#### BindKeyJS(key, js, once=False, virtual_key=True)

Sets a JavaScript function to invoke if a key is pressed.

* **Parameters:**
  * **key** – The key to bind.
  * **js** – The JavaScript to execute when pressed.
  * **once** – If true, the key would be unbinded after first key press.
  * **virtual_key** – If true, also show a button on screen.

#### BindKey(key, handler, args=None, once=False, virtual_key=True)

Sets a key binding to invoke the handler if the key is pressed.

* **Parameters:**
  * **key** – The key to bind.
  * **handler** – The handler to invoke with a single argument (the event
    object).
  * **args** – The arguments to be passed to the handler in javascript,
    which would be json-serialized.
  * **once** – If true, the key would be unbinded after first key press.
  * **virtual_key** – If true, also show a button on screen.

#### UnbindKey(key)

Removes a key binding in frontend JavaScript.

* **Parameters:**
  **key** – The key to unbind.

#### UnbindAllKeys()

Removes all key bindings in frontend JavaScript.

#### GetUILocale()

Returns current enabled locale in UI.

#### PlayAudioFile(audio_file)

Plays an audio file in the given path.

* **Parameters:**
  **audio_file** – The path to the audio file.

#### SetFocus(element_id)

Set focus to the element specified by element_id.

* **Parameters:**
  **element_id** – The HTML DOM id of the element to be focused.

#### SetSelected(element_id)

Set the specified element as selected.

* **Parameters:**
  **element_id** – The HTML DOM id of the element to be selected.

#### Alert(text)

Show an alert box.

* **Parameters:**
  **text** – The text to show in the alert box. Can be an i18n text.

#### HideElement(element_id)

Hide an element by setting display: none.

* **Parameters:**
  **element_id** – The HTML DOM id of the element to be hidden.

#### ShowElement(element_id)

Show an element by setting display: initial.

* **Parameters:**
  **element_id** – The HTML DOM id of the element to be shown.

#### ToggleClass(element_id, dom_class, force=None)

Toggle an element class by classList.toggle().

* **Parameters:**
  * **element_id** – The HTML DOM id of the element to be shown.
  * **dom_class** – The DOM class to be toggled.
  * **force** – Should be None, True or False. If None, toggle the class. If True,
    add the class, else remove the class.

#### ImportHTML(url)

Import a HTML to the test pane.

All other SetHTML / RunJS call would be scheduled after the import is done.

#### WaitKeysOnce(keys, timeout=inf)

Wait for one of the keys to be pressed.

Note that this must NOT be called in the UI thread.

* **Parameters:**
  * **keys** – A key or an array of keys to wait for.
  * **timeout** – Timeout for waiting the key, float(‘inf’) for no timeout.
* **Returns:**
  The key that is pressed, or None if no key is pressed before timeout.

### *class* cros.factory.test.test_ui.StandardUI(event_loop=None)

Standard Web UI that have a template.

This is the default UI used by test_case.TestCase.

#### SetTitle(html)

Sets the title of the test UI.

* **Parameters:**
  **html** – The html content to write.

#### SetState(html, append=False)

Sets the state section in the test UI.

* **Parameters:**
  * **html** – The html to write.
  * **append** – Append html at the end.

#### SetInstruction(html)

Sets the instruction to operator.

* **Parameters:**
  **html** – The html content to write.

#### DrawProgressBar(num_items=1)

Draw the progress bar and set it visible on the Chrome test UI.

* **Parameters:**
  **num_items** – Total number of items for the progress bar. Default to 1 so
  SetProgress can be used to set fraction done.

#### AdvanceProgress()

Advance the progress bar.

#### SetProgress(value)

Set the number of completed items of progress bar.

* **Parameters:**
  **value** – Number of completed items, can be floating point.

#### SetTimerValue(value)

Set the remaining time of timer.

Would show the timer if it’s not already shown.

* **Parameters:**
  **value** – Remaining time.

#### HideTimer(name='timer')

Hide the timer.

* **Parameters:**
  **name** – the name of the timer to hide. If the name is “timer” then it hides
  the countdown timer. If the name is “elapsed-timer” then it hides the
  elapsed timer.

#### SetView(view)

Set the view of the template.

* **Parameters:**
  **view** – The id of the view.

#### ToggleTemplateClass(dom_class, force=None)

Toggle template class by classList.toggle().

* **Parameters:**
  * **dom_class** – The DOM class to be toggled.
  * **force** – Should be None, True or False. If None, toggle the class. If True,
    add the class, else remove the class.

#### StartCountdownTimer(timeout_secs, timeout_handler=None)

Start a countdown timer.

It updates UI for time remaining and calls timeout_handler when timeout.
All works are done in the event loop, and no extra threads are created.

* **Parameters:**
  * **timeout_secs** – Number of seconds to timeout.
  * **timeout_handler** – Callback called when timeout reaches.
* **Returns:**
  A threading.Event that would stop the countdown timer when set.

#### StartFailingCountdownTimer(timeout_secs, error_msg=None)

Start a countdown timer that fail the task after timeout.

* **Parameters:**
  * **timeout_secs** – Number of seconds to timeout.
  * **error_msg** – Error message to fail the test when timeout.
* **Returns:**
  A threading.Event that would stop the countdown timer when set.
