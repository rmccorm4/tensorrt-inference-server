# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
sys.path.append("../common")
sys.path.append("../clients")

import logging

import os
import unittest
import numpy as np
import infer_util as iu

class EnsembleTest(unittest.TestCase):
    def _get_infer_count_per_version(self):
        ctx = ServerStatusContext("localhost:8000", ProtocolType.HTTP, "simple")
        ss = ctx.get_server_status()
        self.assertEqual(os.environ["TENSORRT_SERVER_VERSION"], ss.version)
        self.assertEqual("inference:0", ss.id)
        self.assertEqual(server_status.SERVER_READY, ss.ready_state)
        self.assertEqual(len(ss.model_status), 1)
        self.assertTrue(model_name in ss.model_status,
                        "expected status for model " + model_name)
        self.assertTrue(1 in ss.model_status[model_name].version_status,
                        "expected status for version 1 of model " + model_name)
        self.assertTrue(2 in ss.model_status[model_name].version_status,
                        "expected status for version 2 of model " + model_name)
        infer_count = []
        infer_count.append(ss.model_status[model_name].version_status[1].model_inference_count)
        infer_count.append(ss.model_status[model_name].version_status[2].model_inference_count)
        return infer_count

    def test_ensemble_add_sub(self):
        for bs in (1, 8):
            iu.infer_exact(self, "ensemble_add_sub", (16,), bs,
                                np.int32, np.int32, np.int32)
        
        infer_count = self._get_infer_count_per_version()
        # The two 'simple' versions should have the same infer count
        if (infer_count[0] != infer_count[1]):
            self.assertTrue(False, "unexpeced different infer count for different 'simple' versions")
    
    def test_ensemble_add_sub_one_output(self):
        for bs in (1, 8):
            iu.infer_exact(self, "ensemble_add_sub", (16,), bs,
                                np.int32, np.int32, np.int32,
                                outputs=("OUTPUT0"))
        
        infer_count = self._get_infer_count_per_version()
        # Only 'simple' version 2 should have non-zero infer count
        # as it is in charge of producing OUTPUT0
        if (infer_count[0] != 0):
            self.assertTrue(False, "unexpeced non-zero infer count for 'simple' version 1")
        elif (infer_count[1] == 0):
            self.assertTrue(False, "unexpeced zero infer count for 'simple' version 2")

if __name__ == '__main__':
    logging.basicConfig( stream=sys.stderr )
    unittest.main()
