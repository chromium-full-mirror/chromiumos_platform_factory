from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
GROUP_CODE: CodeType
ONE_TIME_CODE: CodeType
UNIQUE_CODE: CodeType

class Content(_message.Message):
    __slots__ = ["code", "code_type", "device"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    CODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    code: bytes
    code_type: CodeType
    device: str
    def __init__(self, code: _Optional[bytes] = ..., code_type: _Optional[_Union[CodeType, str]] = ..., device: _Optional[str] = ...) -> None: ...

class RegCode(_message.Message):
    __slots__ = ["checksum", "content"]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    checksum: int
    content: Content
    def __init__(self, content: _Optional[_Union[Content, _Mapping]] = ..., checksum: _Optional[int] = ...) -> None: ...

class CodeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
