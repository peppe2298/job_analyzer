from datetime import datetime

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field

from model.agents.abstract.abstract_agent import AbstractAgent

class CheckSkillAgent(AbstractAgent):

    def __init__(self, prompt: PromptTemplate, **kwargs):
        self.prompt: PromptTemplate = prompt
        self.parser: BaseOutputParser = StrOutputParser()
        super().__init__(**kwargs)


    def make_runnable(self, **kwargs) -> Runnable:
        return self.prompt | self.llm | self.parser

class CheckCategoryAgent(AbstractAgent):

    def __init__(self, prompt: PromptTemplate, **kwargs):
        self.prompt: PromptTemplate = prompt
        self.parser: BaseOutputParser = StrOutputParser()
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        return self.prompt | self.llm | self.parser | (lambda x: x.strip().lower() == "true")

class ResultDate(BaseModel):
    date: datetime = Field(..., description="The date when the job announce was posted.")

class DateAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.parser = PydanticOutputParser(ResultDate)
        super().__init__(**kwargs)

    def make_runnable(self) -> Runnable:

        prompt = PromptTemplate.from_template("""your goal is to find out when the job announce was posted
        
        You will have the extraction day and a little text explaining how many time has passed from the posting day to the extraction day.
        
        this is the extraction date: {extraction_date}
        
        this is the text explaining how many time has passed from the posting day to the extraction date: {unformatted_date}
        
        Output: the date when the job announce was posted
        
        """)

        return prompt | self.llm | self.parser | (lambda x: x.date.isoformat())