# Copyright 2021 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Shared utilities for all hwid_api related modules."""

import re
from typing import Optional, Type

from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import common as v3_common
from cros.factory.hwid.v3 import name_pattern_adapter
from cros.factory.probe_info_service.app_engine import protorpc_utils


_KNOWN_BAD_HWIDS = ['DUMMY_HWID', 'dummy_hwid']
_KNOWN_BAD_SUBSTR = [
    '.*TEST.*', '.*CHEETS.*', '^SAMS .*', '.* DEV$', '.*DOGFOOD.*'
]

SUPPORT_STATUS_CASE_OF_HWID_STRING = {
    v3_common.ComponentStatus.supported:
        hwid_api_messages_pb2.ComponentSupportStatus.Case.SUPPORTED,
    v3_common.ComponentStatus.deprecated:
        hwid_api_messages_pb2.ComponentSupportStatus.Case.DEPRECATED,
    v3_common.ComponentStatus.unsupported:
        hwid_api_messages_pb2.ComponentSupportStatus.Case.UNSUPPORTED,
    v3_common.ComponentStatus.unqualified:
        hwid_api_messages_pb2.ComponentSupportStatus.Case.UNQUALIFIED,
    v3_common.ComponentStatus.duplicate:
        hwid_api_messages_pb2.ComponentSupportStatus.Case.DUPLICATE,
}

HWID_STRING_OF_SUPPORT_STATUS_CASE = {
    v: k
    for k, v in SUPPORT_STATUS_CASE_OF_HWID_STRING.items()
}


class GenerateAVLInfoAcceptor(name_pattern_adapter.NameInfoAcceptor[Optional[
    hwid_api_messages_pb2.AvlInfo]]):
  """An acceptor to generate an AvlInfo proto message."""

  def AcceptRegularComp(
      self, cid: int,
      qid: Optional[int]) -> Optional[hwid_api_messages_pb2.AvlInfo]:
    """See base class."""
    return hwid_api_messages_pb2.AvlInfo(cid=cid, qid=qid)

  def AcceptSubcomp(self, cid: int) -> Optional[hwid_api_messages_pb2.AvlInfo]:
    """See base class."""
    return hwid_api_messages_pb2.AvlInfo(cid=cid, is_subcomp=True)

  def AcceptUntracked(self) -> Optional[hwid_api_messages_pb2.AvlInfo]:
    """See base class."""
    return None

  def AcceptLegacy(
      self, raw_comp_name: str) -> Optional[hwid_api_messages_pb2.AvlInfo]:
    """See base class."""
    return None


def FastFailKnownBadHWID(hwid):
  if hwid in _KNOWN_BAD_HWIDS:
    return (hwid_api_messages_pb2.Status.KNOWN_BAD_HWID,
            f'No metadata present for the requested project: {hwid}')

  for regexp in _KNOWN_BAD_SUBSTR:
    if re.search(regexp, hwid):
      return (hwid_api_messages_pb2.Status.KNOWN_BAD_HWID,
              f'No metadata present for the requested project: {hwid}')

  return (hwid_api_messages_pb2.Status.SUCCESS, '')


def ConvertExceptionToStatus(ex):
  if isinstance(ex, KeyError):
    return hwid_api_messages_pb2.Status.NOT_FOUND
  if isinstance(ex, ValueError):
    return hwid_api_messages_pb2.Status.BAD_REQUEST
  return hwid_api_messages_pb2.Status.SERVER_ERROR


def ConvertExceptionToProtoRPCException(ex):
  if isinstance(ex, KeyError):
    return protorpc_utils.ProtoRPCException(
        protorpc_utils.RPCCanonicalErrorCode.NOT_FOUND, str(ex))
  if isinstance(ex, ValueError):
    return protorpc_utils.ProtoRPCException(
        protorpc_utils.RPCCanonicalErrorCode.INVALID_ARGUMENT, str(ex))
  if isinstance(ex, NotImplementedError):
    return protorpc_utils.ProtoRPCException(
        protorpc_utils.RPCCanonicalErrorCode.UNIMPLEMENTED, str(ex))
  return protorpc_utils.ProtoRPCException(
      protorpc_utils.RPCCanonicalErrorCode.INTERNAL, str(ex))


HWIDServiceShardBase: Type = protorpc_utils.CreateProtoRPCServiceShardBase(
    'HWIDServiceShardBase',
    hwid_api_messages_pb2.DESCRIPTOR.services_by_name['HwidService'])
