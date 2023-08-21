# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========

from abc import ABC

from camel.memory.base_memory import BaseMemoryStorage


class BaseShortTermStorage(BaseMemoryStorage, ABC):
    """
    Abstract base class representing the basic operations
    required for short-term memory storage.

    Inherits the basic storage operations from BaseMemoryStorage.
    Any additional short-term specific operations can be added here.
    """
    pass
