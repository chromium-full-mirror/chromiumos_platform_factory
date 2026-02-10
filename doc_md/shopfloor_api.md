# Factory Server and Shopfloor Service

## Overview

To help integration with manufacturing line shopfloor backend systems, we have
defined two server protocols.

One is “[Factory Server](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/umpire/README.md)”
that every DUTs running Chrome OS Factory Software will directly connect to,
and the other is “[Shopfloor Service](https://chromium.googlesource.com/chromiumos/platform/factory/+/HEAD/py/shopfloor/README.md)”
that partner has to implement so the integration work is abstracted with
standardized interface.

## Shopfloor Service API

### *class* cros.factory.shopfloor.xmlrpc_shopfloor_service.ShopfloorService

#### GetVersion()

Returns the version of supported protocol.

#### NotifyStart(data, station)

Notifies shopfloor backend that DUT is starting a manufacturing station.

* **Parameters:**
  * **data** – A FactoryDeviceData instance.
  * **station** – A string to indicate manufacturing station.
* **Returns:**
  A mapping in DeviceData format.

#### NotifyEnd(data, station)

Notifies shopfloor backend that DUT has finished a manufacturing station.

* **Parameters:**
  * **data** – A FactoryDeviceData instance.
  * **station** – A string to indicate manufacturing station.
* **Returns:**
  A mapping in DeviceData format.

#### NotifyEvent(data, event)

Notifies shopfloor backend that the DUT has performed an event.

* **Parameters:**
  * **data** – A FactoryDeviceData instance.
  * **event** – A string to indicate manufacturing event.
* **Returns:**
  A mapping in FactoryDeviceData format.

#### GetDeviceInfo(data)

Returns information about the device’s expected configuration.

* **Parameters:**
  **data** – A FactoryDeviceData instance.
* **Returns:**
  A mapping in DeviceData format.

#### ActivateRegCode(ubind_attribute, gbind_attribute, hwid)

Notifies shopfloor backend that DUT has deployed a registration code.

* **Parameters:**
  * **ubind_attribute** – A string for user registration code.
  * **gbind_attribute** – A string for group registration code.
  * **hwid** – A string for the HWID of the device.
* **Returns:**
  A mapping in DeviceData format.

#### UpdateTestResult(data, test_id, status, details=None)

Sends the specified test result to shopfloor backend.

* **Parameters:**
  * **data** – A FactoryDeviceData instance.
  * **test_id** – A string as identifier of the given test.
  * **status** – A string from TestState; one of PASSED, FAILED, SKIPPED, or
    FAILED_AND_WAIVED.
  * **details** – (optional) A mapping to provide more details, including at least
    ‘error_message’.
* **Returns:**
  A mapping in DeviceData format. If ‘action’ is included, DUT software
  should follow the value to decide how to proceed.

## Factory Server API

### *class* cros.factory.umpire.server.rpc_dut.RootDUTCommands(daemon)

Root DUT (Device Under Test) remote procedures.

Root commands for v1 and v2 compatibilities.

RPC URL:
: [http://umpire_server_address:umpire_port/RPC2](http://umpire_server_address:umpire_port/RPC2)

### *class* cros.factory.umpire.server.rpc_dut.UmpireDUTCommands(daemon)

Umpire DUT remote procedures.

RPC URL:
: [http://umpire_server_address:umpire_port/umpire](http://umpire_server_address:umpire_port/umpire)

#### ListFactoryDrives(pattern)

Lists files that match the pattern in factory drives directory.

* **Parameters:**
  **pattern** – A pattern string for glob to list matched files.
* **Returns:**
  A list of matched files.
* **Raises:**
  **ValueError if caller is trying to query outside factory drives directory.** – 

#### GetFactoryDrive(path)

Gets the assigned factory drive file.

* **Parameters:**
  **path** – A relative path for locating the factory drive.
* **Returns:**
  Content of the factory drive. It is always wrapped in a shopfloor.Binary
  object to provides best flexibility.
* **Raises:**
  * **ValueError if the factory drive does not exist** **or** **is not under** – 
  * **factory drives folder.** – 

#### GetFactoryDrives(namespace=None, name=None)

Gets factory drive components by querying namespace and component name.

* **Parameters:**
  * **namespace** – relative directory path of queried component(s). None if
    they are in root directory.
  * **name** – component name of queried component. None if targeting all
    components under namespace.
* **Returns:**
  Content of the factory drive. It is always wrapped in a shopfloor.Binary
  object to provides best flexibility.
* **Raises:**
  **ValueError if the factory drive does not exist.** – 

#### GetCROSPayloadURL(request, x_umpire_dut)

Gets cros_payload JSON file URL of the matched bundle.

* **Parameters:**
  **x_umpire_dut** – DUT information in GetXUmpireDUT (str) or \_GetXUmpireDUTDict
  (dict) format.
* **Returns:**
  URL of cros_payload JSON file, or empty string if no available bundle.

### *class* cros.factory.umpire.server.rpc_dut.LogDUTCommands(daemon)

DUT log upload procedures.

RPC URL:
: [http://umpire_server_address:umpire_port/umpire](http://umpire_server_address:umpire_port/umpire)

#### AddMetadataToReportBlob(report_blob)

Add metadata.json file to the factory report blob.

* **Parameters:**
  **report_blob** – Blob of compressed report to be stored (must be prepared by
  shopfloor.Binary)
* **Returns:**
  The new report blob

#### UploadReport(serial, report_blob, report_name=None, stage=None)

Uploads a report file.

* **Parameters:**
  * **serial** – A string of device serial number.
  * **report_blob** – Blob of compressed report to be stored (must be prepared by
    shopfloor.Binary)
  * **report_name** – (Optional) Suggested report file name. This is usually
    assigned by factory test client programs (ex, gooftool); however
    server implementations still may use other names to store the report.
  * **stage** – (Optional) Current testing stage: SMT, FAT, RUNIN, FFT, or GRT.
* **Returns:**
  Deferred object that waits for log saving thread to complete.

RPC returns:
: True on success.

* **Raises:**
  * **ValueError if serial is invalid****, or** **other exceptions defined by individual** – 
  * **modules. Note this will be converted to xmlrpc.client.Fault when being** – 
  * **used as a XML-RPC server module.** – 

#### UploadCSVEntry(csv_name, data)

Uploads a list-type data and save in CSV file.

This is usually used for storing device data that should not be associated
with device identifiers (like device serial number), for example
registration codes.

Devices that can be associated with serial numbers should use TestLog.

* **Parameters:**
  * **csv_name** – The base file name of target CSV file, without suffix.
  * **data** – A list or entry to be appended into CSV file.

#### UploadEvent(log_name, chunk)

Uploads a chunk of events.

In addition to append events to a single file, we appends event to a
directory that split on an daily basis.

* **Parameters:**
  * **log_name** – A string of the event log filename. Event logging module creates
    event files with an unique identifier (uuid) as part of the filename.
  * **chunk** – A string containing one or more events. Events are in YAML format
    and separated by a “—” as specified by YAML. A chunk contains one or
    more events with separator.
* **Returns:**
  Deferred object that waits for log saving thread to complete.

RPC returns:
: True on success.

* **Raises:**
  **IOError if unable to save the chunk** **of** **events.** – 

#### SaveAuxLog(name, contents)

Saves an auxiliary log into the umpire_data/aux_logs directory.

In general, this should probably be compressed to save space.

* **Parameters:**
  * **name** – Name of the report.  Any existing log with the same name will be
    overwritten.  Subdirectories are allowed.
  * **contents** – Contents of the report.  If this is binary, it should be
    wrapped in a shopfloor.Binary object.

#### GetFactoryLogPort(request)

Fetches system logs rsync port.
