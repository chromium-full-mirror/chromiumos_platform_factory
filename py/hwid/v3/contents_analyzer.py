# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""This module collects utilities that analyze / validate the HWID DB contents.
"""

from __future__ import annotations

import copy
import dataclasses
import difflib
import enum
import functools
import itertools
import logging
import re
from typing import Any, Callable, ClassVar, Dict, Iterable, List, Mapping, MutableMapping, MutableSequence, NamedTuple, Optional, Tuple, Union

from cros.factory.hwid.v3 import common
from cros.factory.hwid.v3 import database
from cros.factory.hwid.v3 import name_pattern_adapter
from cros.factory.hwid.v3 import rule
from cros.factory.hwid.v3 import yaml_wrapper as yaml
from cros.factory.utils import schema


_BLOCKLIST_DRAM_TAG = set([
    'dram_default',
    'dram_placeholder',
    'a_fake_dram_0gb',
])

_COMP_CLS_ALIAS = {
    'video': 'camera'
}


class ErrorCode(enum.Enum):
  """Enumerate the type of errors."""
  SCHEMA_ERROR = enum.auto()
  CONTENTS_ERROR = enum.auto()
  UNKNOWN_ERROR = enum.auto()
  COMPATIBLE_ERROR = enum.auto()
  CHECKSUM_ERROR = enum.auto()


class Error(NamedTuple):
  """A record class to hold an error message."""
  code: ErrorCode
  message: str


class ProbeValueAlignmentStatus(enum.Enum):
  NO_PROBE_INFO = enum.auto()
  ALIGNED = enum.auto()
  NOT_ALIGNED = enum.auto()

  @classmethod
  def FromProbeValues(cls, values: Optional[Mapping[str, Any]]):
    if values is None:
      # If probe value is null it won't align anyway.
      return cls.NOT_ALIGNED
    if not isinstance(values, rule.AVLProbeValue):
      return cls.NO_PROBE_INFO
    return cls.ALIGNED if values.probe_value_matched else cls.NOT_ALIGNED


def _GetConverterIdentifier(comp_info: database.ComponentInfo) -> Optional[str]:
  if comp_info.values is None:
    return None
  if not isinstance(comp_info.values, rule.AVLProbeValue):
    return None
  return comp_info.values.converter_identifier


class DiffStatus(NamedTuple):
  """Diff stats with the corresponding component in the previous DB."""
  unchanged: bool
  name_changed: bool
  support_status_changed: bool
  values_changed: bool
  prev_comp_name: str
  prev_support_status: str
  probe_value_alignment_status_changed: bool
  prev_probe_value_alignment_status: ProbeValueAlignmentStatus
  converter_changed: bool
  marked_untracked_changed: bool
  probe_info_changed: bool


ComponentNameInfo = name_pattern_adapter.NameInfo


class ValidationReport(NamedTuple):
  errors: List[Error]
  warnings: List[str]

  @classmethod
  def CreateEmpty(cls):
    return cls([], [])


class DBLineAnalysisResult(NamedTuple):

  # yapf: disable
  class ModificationStatus(enum.Enum):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
    NOT_MODIFIED = enum.auto()
    MODIFIED = enum.auto()
    NEWLY_ADDED = enum.auto()

  # yapf: disable
  class Part(NamedTuple):  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable

    class Type(enum.Enum):
      TEXT = enum.auto()
      COMPONENT_NAME = enum.auto()
      COMPONENT_STATUS = enum.auto()

    type: Type
    text: str

    @property
    def reference_id(self):
      return self.text  # Reuse the existing field.

  # yapf: disable
  modification_status: ModificationStatus  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  # yapf: disable
  parts: List[Part]  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable


class HWIDComponentAnalysisResult(NamedTuple):
  comp_cls: str
  comp_name: str
  support_status: str
  is_newly_added: bool
  comp_name_info: ComponentNameInfo
  seq_no: int
  comp_name_with_correct_seq_no: Optional[str]
  null_values: bool
  diff_prev: Optional[DiffStatus]
  link_avl: bool
  probe_value_alignment_status: ProbeValueAlignmentStatus
  skip_avl_check: bool
  marked_untracked: bool


class HWIDSectionTouchCase(enum.Enum):
  TOUCHED = enum.auto()
  UNTOUCHED = enum.auto()


class TouchHWIDSections(NamedTuple):
  image_id_change_status: HWIDSectionTouchCase
  pattern_change_status: HWIDSectionTouchCase
  encoded_fields_change_status: MutableMapping[str, HWIDSectionTouchCase]
  components_change_status: HWIDSectionTouchCase
  rules_change_status: HWIDSectionTouchCase
  framework_version_change_status: HWIDSectionTouchCase


class ChangeAnalysis(NamedTuple):
  precondition_errors: List[Error]
  lines: List[DBLineAnalysisResult]
  hwid_components: Dict[str, HWIDComponentAnalysisResult]
  touched_sections: Optional[TouchHWIDSections] = None


@dataclasses.dataclass
class _LoadedDB:
  load_error: ClassVar[None] = None
  instance: database.Database


@dataclasses.dataclass
class _LoadError:
  load_error: Exception
  instance: ClassVar[None] = None


def _LoadFromDBContents(
    db_contents: str,
    expected_checksum: Optional[str]) -> Union[_LoadedDB, _LoadError]:
  try:
    return _LoadedDB(
        instance=database.Database.LoadData(
            db_contents, expected_checksum=expected_checksum))
  except (schema.SchemaException, common.HWIDException,
          yaml.error.YAMLError) as ex:
    return _LoadError(load_error=ex)


class _HWIDComponentMetadata(NamedTuple):
  name: str
  status: str
  extracted_noseq_comp_name: str
  extracted_seq_no: Optional[str]
  extracted_name_info: ComponentNameInfo
  expected_seq_no: int
  is_newly_added: bool
  null_values: bool
  diff_prev: Optional[DiffStatus]
  link_avl: bool
  probe_value_alignment_status: ProbeValueAlignmentStatus
  skip_avl_check: bool
  from_factory_bundle: bool
  marked_untracked: bool


def _ExtractHWIDComponents(
    curr_db: database.Database, prev_db: Optional[database.Database],
    skip_avl_check_checker: Optional[Callable[[str, database.ComponentInfo],
                                              bool]] = None
) -> MutableMapping[str, MutableSequence[_HWIDComponentMetadata]]:
  ret: MutableMapping[str, MutableSequence[_HWIDComponentMetadata]] = {}
  adapter = name_pattern_adapter.NamePatternAdapter()
  for comp_cls in curr_db.GetComponentClasses():
    ret[comp_cls] = []
    name_pattern = adapter.GetNamePattern(comp_cls)
    prev_items: Iterable[Tuple[str, database.ComponentInfo]] = []
    if prev_db is not None:
      prev_items = prev_db.GetComponents(comp_cls).items()
    curr_items = curr_db.GetComponents(comp_cls).items()

    for expected_seq, (curr_item, prev_item) in enumerate(
        itertools.zip_longest(curr_items, prev_items, fillvalue=None), 1):
      if curr_item is None:
        logging.debug('Remove components (more comps in prev db)')
        break
      comp_name, comp_info = curr_item
      name_info = name_pattern.Matches(comp_name)
      noseq_comp_name, sep, actual_seq = comp_name.partition(
          name_pattern_adapter.SEQ_SEP)
      null_values = comp_info.values is None
      link_avl = isinstance(comp_info.values, rule.AVLProbeValue)
      curr_alignment_status = (
          ProbeValueAlignmentStatus.FromProbeValues(comp_info.values))

      diffstatus = None
      from_factory_bundle = False
      skip_avl_check = (
          skip_avl_check_checker(comp_cls, comp_info)
          if skip_avl_check_checker else False)
      marked_untracked = isinstance(name_info,
                                    name_pattern_adapter.UntrackedNameInfo)
      if prev_item:
        prev_comp_name, prev_comp_info = prev_item
        prev_name_info = name_pattern.Matches(prev_comp_name)
        prev_marked_untracked = isinstance(
            prev_name_info, name_pattern_adapter.UntrackedNameInfo)
        prev_support_status = prev_comp_info.status
        name_changed = prev_comp_name != comp_name
        support_status_changed = prev_support_status != comp_info.status
        # Compare the values instead of the values instance.
        if prev_comp_info.values is None and comp_info.values is None:
          values_changed = False
        elif prev_comp_info.values is None or comp_info.values is None:
          values_changed = True
        else:
          values_changed = dict(prev_comp_info.values) != dict(comp_info.values)
        probe_info_changed = False
        if (isinstance(prev_comp_info.values, rule.AVLProbeValue) and
            isinstance(comp_info.values, rule.AVLProbeValue)):
          probe_info_changed = (
              prev_comp_info.values.probe_info != comp_info.values.probe_info)

        prev_alignment_status = (
            ProbeValueAlignmentStatus.FromProbeValues(prev_comp_info.values))
        probe_value_alignment_status_changed = (
            curr_alignment_status != prev_alignment_status)

        converter_changed = (
            _GetConverterIdentifier(comp_info)
            != _GetConverterIdentifier(prev_comp_info))

        marked_untracked_changed = marked_untracked != prev_marked_untracked

        unchanged = not any([
            name_changed, support_status_changed, values_changed,
            probe_value_alignment_status_changed, converter_changed,
            marked_untracked_changed, probe_info_changed
        ])
        diffstatus = DiffStatus(
            unchanged,
            name_changed,
            support_status_changed,
            values_changed,
            prev_comp_name,
            prev_support_status,
            probe_value_alignment_status_changed,
            prev_alignment_status,
            converter_changed,
            marked_untracked_changed,
            probe_info_changed,
        )
        from_factory_bundle = bool(prev_comp_info.bundle_uuids)
        is_newly_added = False
      else:
        is_newly_added = True

      ret[comp_cls].append(
          _HWIDComponentMetadata(comp_name, comp_info.status, noseq_comp_name,
                                 actual_seq if sep else None, name_info,
                                 expected_seq, is_newly_added, null_values,
                                 diffstatus, link_avl, curr_alignment_status,
                                 skip_avl_check, from_factory_bundle,
                                 marked_untracked))
  return ret


def _ValidateComponentIntegrity(
    validation_report, db_instance: database.Database,
    form_factor: Optional[common.FormFactor] = None) -> None:
  if not form_factor:
    return
  db_comps = db_instance.GetComponentClasses(image_id=db_instance.max_image_id)

  # This is a workaround for checking essential component 'camera' because
  # 'camera' is named 'video' in some old factory branches.
  # TODO(wyuang): remove this WA when all "video" comps factory end.
  for comp_cls, alias in _COMP_CLS_ALIAS.items():
    if comp_cls in db_comps:
      db_comps.add(alias)

  essential_comps = set(common.FORM_FACTOR_COMPS[form_factor])
  for comp_cls in essential_comps - db_comps:
    validation_report.errors.append(
        Error(
            ErrorCode.CONTENTS_ERROR,
            f'Missing component {comp_cls!r} for form factor '
            f'{str(form_factor)!r}.'))


def _ValidateDramIntegrity(validation_report,
                           db_instance: database.Database) -> None:
  for dram_tag, dram_info in db_instance.GetComponents('dram').items():
    if dram_tag in _BLOCKLIST_DRAM_TAG:
      continue
    if dram_info.values is not None and 'size' not in dram_info.values:
      validation_report.errors.append(
          Error(ErrorCode.CONTENTS_ERROR,
                f'{dram_tag!r} does not contain size property'))


def _ValidateChangeOfNewCreation(curr_db: database.Database,
                                 report: ValidationReport) -> bool:
  """Checks if the newly created HWID DB applies up-to-date styles.

  Returns:
    A boolean indicates whether to keep performing the rest of validation
        steps.
  """
  if not curr_db.can_encode:
    report.errors.append(
        Error(
            ErrorCode.CONTENTS_ERROR,
            'The new HWID database should not use legacy pattern.  Please '
            'use "hwid build-database" to prevent from generating legacy '
            'pattern.'))
    return False

  region_field_legacy_info = curr_db.region_field_legacy_info
  if not region_field_legacy_info or any(region_field_legacy_info.values()):
    report.errors.append(
        Error(ErrorCode.CONTENTS_ERROR,
              'Legacy region field is forbidden in any new HWID database.'))
  return True


def _ValidateChangeFromExistingSnapshot(curr_db: database.Database,
                                        prev_db: database.Database,
                                        report: ValidationReport) -> bool:
  """Checks if the HWID DB changes is backward compatible.

  Returns:
    A boolean indicates whether to keep performing the rest of validation
        steps.
  """
  # If the old database follows the new pattern rule, so does the new
  # database.
  if (prev_db.can_encode and not curr_db.can_encode):
    report.errors.append(
        Error(
            ErrorCode.COMPATIBLE_ERROR,
            'The new HWID database should not use legacy pattern. Please '
            'use "hwid update-database" to prevent from generating legacy '
            'pattern.'))
    return False

  visited_patterns = set()
  for image_id in prev_db.image_ids:
    old_bit_mapping = prev_db.GetBitMapping(image_id=image_id)
    if image_id not in curr_db.image_ids:
      report.errors.append(
          Error(ErrorCode.COMPATIBLE_ERROR, f'Image id {image_id} is deleted.'))
      continue
    new_bit_mapping = curr_db.GetBitMapping(image_id=image_id)

    # Make sure all the encoded fields in the existing patterns are not
    # changed.
    for index, (element_old, element_new) in enumerate(
        zip(old_bit_mapping, new_bit_mapping)):
      if element_new != element_old:
        report.errors.append(
            Error(
                ErrorCode.COMPATIBLE_ERROR,
                f'Bit pattern mismatch found at bit {index} (encoded '
                f'field={element_old[0]}). If you are trying to append new '
                'bit(s), be sure to create a new bit pattern field instead '
                'of simply incrementing the last field.'))

    # Make sure no new component field is added to existing pattern after
    # PVT.
    pattern_id = curr_db.GetPattern(image_id).idx
    image_name = curr_db.GetImageName(image_id)
    if (pattern_id not in visited_patterns and
        re.fullmatch(r'(PVT|MP).*', image_name, flags=re.IGNORECASE)):
      visited_patterns.add(pattern_id)
      old_field_set = set(prev_db.GetEncodedFieldsBitLength(image_id))
      new_field_set = set(curr_db.GetEncodedFieldsBitLength(image_id))
      added_fields = new_field_set - old_field_set
      if added_fields:
        report.errors.append(
            Error(
                ErrorCode.COMPATIBLE_ERROR,
                f'New component class field(s)({added_fields}) should not be '
                f'appended in the existing pattern(#{pattern_id}) except in '
                'early phases. Please create a new pattern instead.'))

  old_reg_field_legacy_info = prev_db.region_field_legacy_info
  new_reg_field_legacy_info = curr_db.region_field_legacy_info
  for field_name, is_legacy_style in new_reg_field_legacy_info.items():
    orig_is_legacy_style = old_reg_field_legacy_info.get(field_name)
    if orig_is_legacy_style is None:
      if is_legacy_style:
        report.errors.append(
            Error(
                ErrorCode.CONTENTS_ERROR,
                'New region field should be constructed by new style yaml '
                'tag.'))
    else:
      if orig_is_legacy_style != is_legacy_style:
        report.errors.append(
            Error(ErrorCode.COMPATIBLE_ERROR,
                  'Style of existing region field should remain unchanged.'))
  return True


def _ValidateChangeOfComponents(curr_db: database.Database,
                                prev_db: Optional[database.Database],
                                report: ValidationReport):
  """Check if modified (created) components are valid."""
  for comp_cls, comps in _ExtractHWIDComponents(curr_db, prev_db).items():
    for comp in comps:
      if comp.extracted_seq_no is not None:
        expected_comp_name = ''.join([
            comp.extracted_noseq_comp_name, name_pattern_adapter.SEQ_SEP,
            str(comp.expected_seq_no)
        ])
        if expected_comp_name != comp.name:
          report.errors.append(
              Error(
                  ErrorCode.CONTENTS_ERROR,
                  'Invalid component name with sequence number, please '
                  f'modify it from {comp.name!r} to {expected_comp_name!r}'
                  '.'))
          continue
      if not comp.is_newly_added:
        assert comp.diff_prev is not None
        if comp.diff_prev.name_changed and comp.diff_prev.values_changed:
          report.errors.append(
              Error(
                  ErrorCode.COMPATIBLE_ERROR, 'Modifying both the component '
                  f'name ({comp.diff_prev.prev_comp_name!r} -> {comp.name!r}) '
                  'and values often causes compatibility issues. Is this '
                  'change proposal mistakenly based on a legacy HWID bundle?'))
      if comp.is_newly_added and prev_db is not None:
        comp_info = curr_db.GetComponents(comp_cls)[comp.name]
        try:
          duplicate_name = prev_db.GetComponentNameByHash(
              comp_cls, comp_info.comp_hash)
          report.errors.append(
              Error(
                  ErrorCode.COMPATIBLE_ERROR,
                  'Adding component with the same probe value is invalid. '
                  f'Please rename {duplicate_name!r} to {comp.name!r} '
                  'instead.'))
        except KeyError:
          pass


def _AnalyzeDBLines(curr_db: database.Database,
                    prev_db: Optional[database.Database], db_contents_patcher,
                    all_placeholders, db_placeholder_options):
  dumped_db_lines = db_contents_patcher(
      curr_db.DumpDataWithoutChecksum(
          suppress_support_status=False,
          magic_placeholder_options=db_placeholder_options)).splitlines()

  no_placeholder_dumped_db_lines = db_contents_patcher(
      curr_db.DumpDataWithoutChecksum(
          suppress_support_status=False)).splitlines()
  if len(dumped_db_lines) != len(no_placeholder_dumped_db_lines):
    # Unexpected case, skip deriving the line diffs.
    diff_view_line_it = itertools.repeat('  ', len(dumped_db_lines))
  elif not prev_db:
    diff_view_line_it = itertools.repeat('  ', len(dumped_db_lines))
  else:
    prev_db_contents_lines = db_contents_patcher(
        prev_db.DumpDataWithoutChecksum(
            suppress_support_status=False)).splitlines()
    # yapf: disable
    diff_view_line_it = difflib.ndiff(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
    # yapf: enable
        prev_db_contents_lines, no_placeholder_dumped_db_lines, charjunk=None)

  removed_line_count = 0

  splitter = _LineSplitter(
      all_placeholders,
      # yapf: disable
      functools.partial(DBLineAnalysisResult.Part,  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
                        # yapf: enable
                        # yapf: disable
                        DBLineAnalysisResult.Part.Type.TEXT))  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
  # yapf: enable
  line_analysis_result = []
  for line in dumped_db_lines:
    while True:
      diff_view_line = next(diff_view_line_it)
      if diff_view_line.startswith('? '):
        continue
      if not diff_view_line.startswith('- '):
        break
      removed_line_count += 1
    if diff_view_line.startswith('  '):
      removed_line_count = 0
      # yapf: disable
      mod_status = DBLineAnalysisResult.ModificationStatus.NOT_MODIFIED  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    elif removed_line_count > 0:
      removed_line_count -= 1
      # yapf: disable
      mod_status = DBLineAnalysisResult.ModificationStatus.MODIFIED  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable
    else:
      # yapf: disable
      mod_status = DBLineAnalysisResult.ModificationStatus.NEWLY_ADDED  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
      # yapf: enable

    parts = splitter.SplitText(line)
    line_analysis_result.append(DBLineAnalysisResult(mod_status, parts))
  return line_analysis_result


def _FillTouchedSections(
    curr_db: database.Database,
    prev_db: Optional[database.Database]) -> Optional[TouchHWIDSections]:
  if prev_db is None:
    return None

  image_id_change_status = HWIDSectionTouchCase.UNTOUCHED
  pattern_change_status = HWIDSectionTouchCase.UNTOUCHED
  components_change_status = HWIDSectionTouchCase.UNTOUCHED
  rules_change_status = HWIDSectionTouchCase.UNTOUCHED
  framework_version_change_status = HWIDSectionTouchCase.UNTOUCHED
  encoded_fields_change_status = {}
  if prev_db.image_ids != curr_db.image_ids:
    image_id_change_status = HWIDSectionTouchCase.TOUCHED
    pattern_change_status = HWIDSectionTouchCase.TOUCHED
  else:
    for image_id in prev_db.image_ids:
      if prev_db.GetImageName(image_id) != curr_db.GetImageName(image_id):
        image_id_change_status = HWIDSectionTouchCase.TOUCHED
        break

    for image_id in prev_db.image_ids:
      if prev_db.GetEncodingScheme(image_id) != curr_db.GetEncodingScheme(
          image_id):
        pattern_change_status = HWIDSectionTouchCase.TOUCHED
        break
      if prev_db.GetBitMapping(image_id=image_id) != curr_db.GetBitMapping(
          image_id=image_id):
        pattern_change_status = HWIDSectionTouchCase.TOUCHED
        break

  curr_encoded_fields = set(curr_db.encoded_fields)
  prev_encoded_fields = set(prev_db.encoded_fields)
  for encoded_field in curr_encoded_fields - prev_encoded_fields:
    encoded_fields_change_status[encoded_field] = HWIDSectionTouchCase.TOUCHED
  for encoded_field in curr_encoded_fields & prev_encoded_fields:
    if prev_db.GetEncodedField(encoded_field) != curr_db.GetEncodedField(
        encoded_field):
      encoded_fields_change_status[encoded_field] = (
          HWIDSectionTouchCase.TOUCHED)
    else:
      encoded_fields_change_status[encoded_field] = (
          HWIDSectionTouchCase.UNTOUCHED)

  if prev_db.GetComponentClasses() != curr_db.GetComponentClasses():
    components_change_status = HWIDSectionTouchCase.TOUCHED
  else:
    for comp_cls in prev_db.GetComponentClasses():
      if prev_db.GetComponents(comp_cls) != curr_db.GetComponents(comp_cls):
        components_change_status = HWIDSectionTouchCase.TOUCHED
        break

  if prev_db.device_info_rules != curr_db.device_info_rules:
    rules_change_status = HWIDSectionTouchCase.TOUCHED
  elif prev_db.verify_rules != curr_db.verify_rules:
    rules_change_status = HWIDSectionTouchCase.TOUCHED

  if prev_db.framework_version != curr_db.framework_version:
    framework_version_change_status = HWIDSectionTouchCase.TOUCHED

  return TouchHWIDSections(image_id_change_status, pattern_change_status,
                           encoded_fields_change_status,
                           components_change_status, rules_change_status,
                           framework_version_change_status)


class ContentsAnalyzer:
  _curr_db: Union[_LoadedDB, _LoadError]
  _prev_db: Optional[Union[_LoadedDB, _LoadError]]

  def __init__(self, curr_db_contents: str,
               expected_curr_db_checksum: Optional[str],
               prev_db_contents: Optional[str]):
    self._curr_db = _LoadFromDBContents(curr_db_contents,
                                        expected_curr_db_checksum)
    self._prev_db = (
        _LoadFromDBContents(prev_db_contents, None)
        if prev_db_contents is not None else None)

  @property
  def curr_db_instance(self) -> Optional[database.Database]:
    return self._curr_db.instance

  @property
  def prev_db_instance(self) -> Optional[database.Database]:
    return self._prev_db.instance if self._prev_db else None

  def ValidateIntegrity(
      self,
      form_factor: Optional[common.FormFactor] = None) -> ValidationReport:
    """Validates the current HWID DB.

    Args:
      kwargs: keyword arguments that will be passed to the validation functions.

    Returns:
      A ValidationReport instance.
    """
    report = ValidationReport.CreateEmpty()
    if not isinstance(self._curr_db, _LoadedDB):
      report.errors.append(
          Error(ErrorCode.SCHEMA_ERROR, str(self._curr_db.load_error)))
      return report

    _ValidateDramIntegrity(report, self._curr_db.instance)
    _ValidateComponentIntegrity(report, self._curr_db.instance, form_factor)
    return report

  def ValidateChange(self, ignore_invalid_old_db=False) -> ValidationReport:
    """Validates the change between the current HWID DB and the previous one."""
    report = ValidationReport.CreateEmpty()
    if not isinstance(self._curr_db, _LoadedDB):
      report.errors.append(
          Error(ErrorCode.SCHEMA_ERROR, str(self._curr_db.load_error)))
      return report

    if self._prev_db is None:
      if not _ValidateChangeOfNewCreation(self._curr_db.instance, report):
        return report
    elif not isinstance(self._prev_db, _LoadedDB):
      if ignore_invalid_old_db:
        report.warnings.append(
            'The previous version of HWID database is an incompatible version '
            f'(exception: {self._prev_db.load_error}), ignore the pattern '
            'check.')
      else:
        report.errors.append(
            Error(
                ErrorCode.UNKNOWN_ERROR,
                'Failed to load the previous version of '
                f'HWID DB: {self._prev_db.load_error}'))
        return report
    else:
      if not _ValidateChangeFromExistingSnapshot(
          self._curr_db.instance, self._prev_db.instance, report):
        return report
    _ValidateChangeOfComponents(self._curr_db.instance, self.prev_db_instance,
                                report)
    return report

  def ValidateFirmwareComponents(self):
    """Check if modified (created) firmware components are valid."""
    report = ValidationReport.CreateEmpty()
    if not isinstance(self._curr_db, _LoadedDB):
      report.errors.append(
          Error(ErrorCode.SCHEMA_ERROR, str(self._curr_db.load_error)))
      return report

    for comps in _ExtractHWIDComponents(self._curr_db.instance,
                                        self.prev_db_instance).values():
      for comp in comps:
        if (comp.from_factory_bundle and comp.diff_prev and
            (comp.diff_prev.name_changed or comp.diff_prev.values_changed)):
          assert not comp.is_newly_added
          report.errors.append(
              Error(
                  ErrorCode.CONTENTS_ERROR, 'Modifying firmware component '
                  f'{comp.diff_prev.prev_comp_name!r} which is generated from '
                  'the system. Is this change proposal mistakenly based on a '
                  'legacy HWID bundle?'))
    return report

  def AnalyzeChange(
      self, db_contents_patcher: Optional[Callable[[str], str]],
      require_hwid_db_lines: bool,
      skip_avl_check_checker: Optional[Callable[[str, database.ComponentInfo],
                                                bool]] = None
  ) -> ChangeAnalysis:
    """Analyzes the HWID DB change.

    Args:
      db_contents_patcher: An optional function that patches / removes the
          header of the given HWID DB contents.  This argument is ignored when
          require_hwid_db_lines is False.
      skip_avl_check_checker: An optional function that checks if the component
          does not require AVL check (e.g. known software nodes).
      require_hwid_db_lines: A flag indicating if DB line analysis is required.

    Returns:
      An instance of `ChangeAnalysis`.
    """
    if not isinstance(self._curr_db, _LoadedDB):
      report = ChangeAnalysis([], [], {})
      report.precondition_errors.append(
          Error(ErrorCode.SCHEMA_ERROR, str(self._curr_db.load_error)))
      return report

    # To locate the HWID component name / status text part in the HWID DB
    # contents, we first dump a specialized HWID DB which has all cared parts
    # replaced by some magic placeholders.  Then we parse the raw string to
    # find out the location of those fields.

    all_comps = _ExtractHWIDComponents(
        self._curr_db.instance, self.prev_db_instance, skip_avl_check_checker)
    all_placeholders = {}
    db_placeholder_options = database.MagicPlaceholderOptions({})
    hwid_components = {}
    for comp_cls, comps in all_comps.items():
      for comp in comps:
        comp_name_replacer = _LineSplitter.GeneratePlaceholderKey(
            f'component-{comp_cls}-{comp.name}')
        comp_status_replacer = _LineSplitter.GeneratePlaceholderKey(
            f'support_status-{comp_cls}-{comp.name}')
        # yapf: disable
        db_placeholder_options.components[(comp_cls, comp.name)] = (  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
            database.MagicPlaceholderComponentOptions(comp_name_replacer,
                                                      comp_status_replacer))

        # yapf: disable
        all_placeholders[comp_name_replacer] = DBLineAnalysisResult.Part(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
            # yapf: disable
            DBLineAnalysisResult.Part.Type.COMPONENT_NAME, comp_name_replacer)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable
        # yapf: disable
        all_placeholders[comp_status_replacer] = DBLineAnalysisResult.Part(  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
            # yapf: enable
            # yapf: disable
            DBLineAnalysisResult.Part.Type.COMPONENT_STATUS, comp_name_replacer)  # type: ignore #TODO(b/338318729) Fixit! # pylint: disable=line-too-long
        # yapf: enable

        if (comp.extracted_seq_no is not None and
            comp.extracted_seq_no != str(comp.expected_seq_no)):
          comp_name_with_correct_seq_no = ''.join([
              comp.extracted_noseq_comp_name, name_pattern_adapter.SEQ_SEP,
              str(comp.expected_seq_no)
          ])
        else:
          comp_name_with_correct_seq_no = None
        hwid_components[comp_name_replacer] = (
            HWIDComponentAnalysisResult(
                comp_cls, comp.name, comp.status, comp.is_newly_added,
                comp.extracted_name_info, comp.expected_seq_no,
                comp_name_with_correct_seq_no, comp.null_values, comp.diff_prev,
                comp.link_avl, comp.probe_value_alignment_status,
                comp.skip_avl_check, comp.marked_untracked))

    if require_hwid_db_lines:
      if db_contents_patcher is None:
        raise ValueError(('db_contents_patcher should not be None when '
                          'require_hwid_db_lines is set to True'))
      lines = _AnalyzeDBLines(self._curr_db.instance, self.prev_db_instance,
                              db_contents_patcher, all_placeholders,
                              db_placeholder_options)
    else:
      lines = []

    touched_sections = _FillTouchedSections(self._curr_db.instance,
                                            self.prev_db_instance)
    return ChangeAnalysis([], lines, hwid_components, touched_sections)


class _LineSplitter:

  _PLACEHOLDER_KEY_MATCHER = re.compile(r'(x@@@@[^@]+@@y@)')

  @classmethod
  def GeneratePlaceholderKey(cls, placeholder_identity):
    # Prefix "x" prevents yaml from quoting the string.  The "y" in the
    # suffix part prevents the overlapped search result.
    return f'x@@@@{placeholder_identity.replace("@", "<at>")}@@y@'

  def __init__(self, placeholders, text_part_factory):
    self._placeholders = placeholders
    self._text_part_factory = text_part_factory

  def SplitText(self, text):
    parts = []
    curr_pos = re_curr_pos = 0
    while True:
      matched_result = self._PLACEHOLDER_KEY_MATCHER.search(
          text, pos=re_curr_pos)
      if not matched_result:
        break
      placeholder_key = matched_result[0]
      try:
        placeholder_sample = self._placeholders[placeholder_key]
      except KeyError:
        logging.warning(
            'Matched unexpected placeholder string: %s, maybe the '
            'prefix / suffix are not magical enough?', placeholder_key)
        re_curr_pos = matched_result.end()
        continue
      if curr_pos < matched_result.start():
        parts.append(
            self._text_part_factory(text[curr_pos:matched_result.start()]))
      parts.append(copy.deepcopy(placeholder_sample))
      curr_pos = re_curr_pos = matched_result.end()
    if curr_pos < len(text):
      parts.append(self._text_part_factory(text[curr_pos:]))
    return parts
