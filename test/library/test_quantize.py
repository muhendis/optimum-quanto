# Copyright 2024 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import torch
from helpers import assert_similar, device_eq, random_tensor

from optimum.quanto import (
    absmax_scale,
    qfloat8,
    qfloat8_e4m3fn,
    qfloat8_e5m2,
    qint8,
)


@pytest.mark.parametrize("input_shape", [(32, 32), (32, 10, 32)])
@pytest.mark.parametrize("dtype", [torch.float16, torch.float32], ids=["fp16", "fp32"])
@pytest.mark.parametrize("qtype", [qint8], ids=["qint8"])
@pytest.mark.parametrize(
    "axis",
    [None, 0, -1],
    ids=["per-tensor", "first-axis", "last-axis"],
)
def test_symmetric_quantize_int(input_shape, dtype, qtype, axis, device):
    a = random_tensor(input_shape, dtype=dtype).to(device)
    scale = absmax_scale(a, qtype=qtype, axis=axis)
    data = torch.ops.quanto.quantize_symmetric(a, dtype=qtype.dtype, axis=axis, scale=scale)
    assert data.dtype == qtype.dtype
    assert device_eq(data.device, device)
    assert_similar(a, data * scale)


@pytest.mark.skip_device("mps")
@pytest.mark.parametrize("input_shape", [(32, 32), (32, 10, 32)])
@pytest.mark.parametrize("dtype", [torch.float16, torch.float32], ids=["fp16", "fp32"])
@pytest.mark.parametrize(
    "qtype", [qfloat8, qfloat8_e4m3fn, qfloat8_e5m2], ids=["qfloat8", "qfloat8_e4m3fn", "qfloat8_e5m2"]
)
@pytest.mark.parametrize(
    "axis",
    [None, 0, -1],
    ids=["per-tensor", "first-axis", "last-axis"],
)
def test_symmetric_quantize_float8(input_shape, dtype, qtype, axis, device):
    a = random_tensor(input_shape, dtype=dtype).to(device)
    scale = absmax_scale(a, qtype=qtype, axis=axis)
    data = torch.ops.quanto.quantize_symmetric(a, dtype=qtype.dtype, axis=axis, scale=scale)
    assert data.dtype == qtype.dtype
    assert device_eq(data.device, device)
    assert_similar(a, data.to(dtype) * scale, atol=5e-3)
