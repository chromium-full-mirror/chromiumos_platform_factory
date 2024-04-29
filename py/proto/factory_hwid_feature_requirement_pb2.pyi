from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BrandFeatureRequirementSpec(_message.Message):
    __slots__ = ["feature_enablement_case", "feature_version", "profiles"]
    class FeatureEnablementCase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class Profile(_message.Message):
        __slots__ = ["description", "encoding_requirements"]
        class EncodingRequirement(_message.Message):
            __slots__ = ["bit_locations", "description", "required_values"]
            BIT_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
            DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
            REQUIRED_VALUES_FIELD_NUMBER: _ClassVar[int]
            bit_locations: _containers.RepeatedScalarFieldContainer[int]
            description: str
            required_values: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, description: _Optional[str] = ..., bit_locations: _Optional[_Iterable[int]] = ..., required_values: _Optional[_Iterable[str]] = ...) -> None: ...
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        ENCODING_REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
        description: str
        encoding_requirements: _containers.RepeatedCompositeFieldContainer[BrandFeatureRequirementSpec.Profile.EncodingRequirement]
        def __init__(self, description: _Optional[str] = ..., encoding_requirements: _Optional[_Iterable[_Union[BrandFeatureRequirementSpec.Profile.EncodingRequirement, _Mapping]]] = ...) -> None: ...
    FEATURE_ENABLEMENT_CASE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_ENABLEMENT_CASE_UNSPECIFIC: BrandFeatureRequirementSpec.FeatureEnablementCase
    FEATURE_MUST_ENABLED: BrandFeatureRequirementSpec.FeatureEnablementCase
    FEATURE_MUST_NOT_ENABLED: BrandFeatureRequirementSpec.FeatureEnablementCase
    FEATURE_VERSION_FIELD_NUMBER: _ClassVar[int]
    MIXED: BrandFeatureRequirementSpec.FeatureEnablementCase
    PROFILES_FIELD_NUMBER: _ClassVar[int]
    feature_enablement_case: BrandFeatureRequirementSpec.FeatureEnablementCase
    feature_version: int
    profiles: _containers.RepeatedCompositeFieldContainer[BrandFeatureRequirementSpec.Profile]
    def __init__(self, feature_version: _Optional[int] = ..., profiles: _Optional[_Iterable[_Union[BrandFeatureRequirementSpec.Profile, _Mapping]]] = ..., feature_enablement_case: _Optional[_Union[BrandFeatureRequirementSpec.FeatureEnablementCase, str]] = ...) -> None: ...

class FeatureRequirementSpec(_message.Message):
    __slots__ = ["brand_specs"]
    class BrandSpecsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: BrandFeatureRequirementSpec
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[BrandFeatureRequirementSpec, _Mapping]] = ...) -> None: ...
    BRAND_SPECS_FIELD_NUMBER: _ClassVar[int]
    brand_specs: _containers.MessageMap[str, BrandFeatureRequirementSpec]
    def __init__(self, brand_specs: _Optional[_Mapping[str, BrandFeatureRequirementSpec]] = ...) -> None: ...
