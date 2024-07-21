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
from typing import Optional

from camel.messages.base import BaseMessage

from .base_agent_system import BaseAgentSystem


class MultiAgent(BaseAgentSystem):
    """
    A multi-agent system that processes prompts using a ChatAgent.

    This class implements the BaseAgentSystem interface and provides
    functionality to interact with a single AI agent

    Attributes:
        system_message (str): The system message used to initialize the
        ChatAgent. Defaults to "You are a helpful assistant." if not provided.

    Example:
        agent = MultiAgent("You are an expert in Python programming.")
        response = agent.run("What are the benefits of using decorators?")
    """

    def __init__(self, agents, system_message: Optional[str] = None) -> None:
        self.system_message = system_message or "You are a helpful assistant."
        assistant_sys_msg = BaseMessage.make_assistant_message(
            role_name="Assistant",
            content=self.system_message,
        )
        # self.agent = ChatAgent(
        #     assistant_sys_msg,
        #     model=OpenAIModel(
        #         ModelType.GPT_4, model_config_dict={"max_tokens": 1000}
        #     ),
        # )

    def run(self, prompt: str) -> str:
        """
        Execute the single agent system with the given prompt.

        Args:
            prompt (str): The input prompt to be processed by the agent.

        Returns:
            str: The response generated by the agent.
        """
        for agent in self.agents:
            agent.reset()

        user_msg = BaseMessage.make_user_message(
            role_name="User", content=prompt
        )
        assistant_response = self.agent.step(user_msg)

        return assistant_response.msg
