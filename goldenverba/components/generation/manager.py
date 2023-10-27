from goldenverba.components.generation.interface import Generator
from goldenverba.components.generation.GPT4Generator import GPT4Generator
from goldenverba.components.generation.GPT3Generator import GPT3Generator
from goldenverba.components.generation.Llama2Generator import Llama2Generator

import tiktoken


from wasabi import msg


class GeneratorManager:
    def __init__(self):
        self.generators: dict[str, Generator] = {
            "GPT4Generator": GPT4Generator(),
            "GPT3Generator": GPT3Generator(),
            "Llama2Generator": Llama2Generator(),
        }
        self.selected_generator: Generator = self.generators["GPT3Generator"]

    async def generate(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = {},
    ) -> str:
        """Generate an answer based on a list of queries and list of contexts, include conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns str - Answer generated by the Generator
        """
        return await self.selected_generator.generate(
            queries, context, self.truncate_conversation_items(conversation)
        )

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = {},
    ) -> str:
        """Generate an answer based on a list of queries and list of contexts, include conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns str - Answer generated by the Generator
        """
        async for result in self.selected_generator.generate_stream(
            queries, context, self.truncate_conversation_items(conversation)
        ):
            yield result

    def truncate_conversation_dicts(conversation_dicts: list, max_tokens: int) -> list:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        accumulated_tokens = 0
        truncated_conversation_dicts = []

        # Start with the newest conversations
        for item_dict in reversed(conversation_dicts):
            item_tokens = encoding.encode(item_dict["content"], disallowed_special=())

            # If adding the entire new item exceeds the max tokens
            if accumulated_tokens + len(item_tokens) > max_tokens:
                # Calculate how many tokens we can add from this item
                remaining_space = max_tokens - accumulated_tokens
                truncated_content = encoding.decode(item_tokens[:remaining_space])

                # Create a new truncated item dictionary
                truncated_item_dict = {
                    "type": item_dict["type"],
                    "content": truncated_content,
                    "typewriter": item_dict["typewriter"],
                }

                truncated_conversation_dicts.append(truncated_item_dict)
                break

            truncated_conversation_dicts.append(item_dict)
            accumulated_tokens += len(item_tokens)

        # The list has been built in reverse order so we reverse it again
        print(list(reversed(truncated_conversation_dicts)))
        return list(reversed(truncated_conversation_dicts))

    def set_generator(self, generator: str) -> bool:
        if generator in self.generators:
            self.selected_generator = self.generators[generator]
            return True
        else:
            msg.warn(f"Generator {generator} not found")
            return False

    def get_generators(self) -> dict[str, Generator]:
        return self.generators
