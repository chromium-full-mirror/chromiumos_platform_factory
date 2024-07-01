# Copyright 2024 The ChromiumOS Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import os.path
import unittest

from cros.factory.hwid.service.appengine.data import dlm_component_list
from cros.factory.hwid.service.appengine.proto import hwid_api_messages_pb2  # pylint: disable=no-name-in-module
from cros.factory.hwid.v3 import database


_DlmComponentMsg = hwid_api_messages_pb2.DlmComponentInfo
_AvlInfoMsg = hwid_api_messages_pb2.AvlInfo

GOLDEN_HWIDV3_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'testdata',
    'v3-update-comp.yaml')


class DlmComponentListTest(unittest.TestCase):

  def testPathComponentList_Success(self):
    db = database.Database.LoadFile(GOLDEN_HWIDV3_FILE, verify_checksum=False)
    comp_list = [
        _DlmComponentMsg(
            avl_info=_AvlInfoMsg(cid=1), related_hwid_classes=['comp_cls1'],
            has_claim_for_pvt_or_mp_use=True, claim_for_pvt_or_mp_use=True),
        _DlmComponentMsg(
            avl_info=_AvlInfoMsg(cid=1,
                                 qid=1), related_hwid_classes=['comp_cls1'],
            has_claim_for_pvt_or_mp_use=True, claim_for_pvt_or_mp_use=False),
        _DlmComponentMsg(
            avl_info=_AvlInfoMsg(cid=2, is_subcomp=True),
            related_hwid_classes=['comp_cls1'],
            has_claim_for_pvt_or_mp_use=True, claim_for_pvt_or_mp_use=False),
    ]

    new_db = dlm_component_list.PatchComponentList(db, comp_list)

    comps = new_db.GetComponents('comp_cls1')
    self.assertEqual(comps['comp_cls1_1'].status, 'supported')
    self.assertEqual(comps['comp_cls1_1_1'].status, 'unsupported')
    self.assertEqual(comps['comp_cls1_subcomp_2'].status, 'deprecated')

  def testPathComponentList_ExcludeDefaultComps(self):
    db = database.Database.LoadFile(GOLDEN_HWIDV3_FILE, verify_checksum=False)
    comp_list = [
        _DlmComponentMsg(
            avl_info=_AvlInfoMsg(cid=3), related_hwid_classes=['comp_cls1'],
            has_claim_for_pvt_or_mp_use=True, claim_for_pvt_or_mp_use=True),
    ]

    new_db = dlm_component_list.PatchComponentList(db, comp_list)

    comps = new_db.GetComponents('comp_cls1')
    self.assertEqual(comps['comp_cls1_3'].status, 'unqualified')


if __name__ == '__main__':
  unittest.main()
