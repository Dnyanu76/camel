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
from typing import Any, Dict, List, Optional, Union

from vllm import LLM, SamplingParams
from vllm.multimodal.utils import fetch_image

from camel.configs import VLLM_API_PARAMS, VLLMConfig
from camel.messages import OpenAIMessage
from camel.models import BaseModelBackend
from camel.types import ChatCompletion, ChatCompletionChunk, ModelType
from camel.utils import BaseTokenCounter, OpenAITokenCounter


class VLLMModel(BaseModelBackend):
    def __init__(
        self,
        model_type: ModelType,
        model_config_dict: Dict[str, Any],
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        token_counter: Optional[BaseTokenCounter] = None,
    ) -> None:
        super().__init__(
            model_type=model_type,
            model_config_dict=model_config_dict,
            api_key=api_key,
            url=url,
        )
        self._token_counter = token_counter
        self.config = VLLMConfig(**model_config_dict)
        self.llm = LLM(
            model=self.config.model,
            trust_remote_code=self.config.trust_remote_code,
            max_model_len=self.config.max_model_len,
            limit_mm_per_prompt=self.config.limit_mm_per_prompt,
        )

    @property
    def token_counter(self) -> BaseTokenCounter:
        r"""Initialize the token counter for the model backend.

        Returns:
            BaseTokenCounter: The token counter following the model's
                tokenization style.
        """
        if not self._token_counter:
            self._token_counter = OpenAITokenCounter(ModelType.GPT_4O_MINI)
        return self._token_counter

    def run(
        self,
        messages: List[OpenAIMessage],
    ) -> Union[ChatCompletion, ChatCompletionChunk]:
        question = messages[-1]['content']
        image_urls = self.config.image_urls
        image_data = [fetch_image(url) for url in image_urls]

        sampling_params = SamplingParams(
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stop_token_ids=self.config.stop_token_ids,
        )

        if self.config.method == "generate":
            placeholders = "\n".join(
                f"<|image_{i}|>" for i, _ in enumerate(image_urls, start=1)
            )
            prompt = (
                f"<|user|>\n{placeholders}\n{question}<|end|>\n<|assistant|>\n"
            )
            outputs = self.llm.generate(
                {"prompt": prompt, "multi_modal_data": {"image": image_data}},
                sampling_params=sampling_params,
            )
        elif self.config.method == "chat":
            outputs = self.llm.chat(
                [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": question}]
                        + [
                            {"type": "image_url", "image_url": {"url": url}}
                            for url in image_urls
                        ],
                    }
                ],
                sampling_params=sampling_params,
            )
        else:
            raise ValueError(f"Invalid method: {self.config.method}")

        # Convert vLLM output to OpenAI-like format
        response = ChatCompletion(
            id="vllm_response",
            object="chat.completion",
            created=0,
            model=self.config.model,
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": outputs[0].outputs[0].text,
                    },
                    "finish_reason": "stop",
                }
            ],
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        )
        return response

    def check_model_config(self):
        for param in self.model_config_dict:
            if param not in VLLM_API_PARAMS:
                raise ValueError(
                    f"Unexpected argument `{param}` is "
                    "input into VLLM model backend."
                )

    @property
    def token_limit(self) -> int:
        return self.config.max_model_len

    @property
    def stream(self) -> bool:
        return False  # VLLM doesn't support streaming in this implementation
