from abc import ABC, abstractmethod

from langchain_core.language_models import BaseLLM
from langchain_core.runnables import Runnable
from langchain_ollama import OllamaLLM


class AbstractAgent(ABC):

    def __init__(self, **kwargs):
        super().__init__()
        self.runnable: Runnable = self.make_runnable()

    @property
    def llm(self) -> BaseLLM:
        return OllamaLLM(model = "gemma2", temperature = 0)

    @abstractmethod
    def make_runnable(self) -> Runnable:
        pass


    def invoke(self, input_variable: dict):
        return self.runnable.invoke(input=input_variable)