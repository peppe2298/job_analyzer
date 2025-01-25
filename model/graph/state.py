from typing import List, TypedDict, Annotated


class Field:
    def __init__(self, name, required=False):
        self.name = name
        self.required = required

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.name == other.name
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

class HardSkill(Field):
    pass

class Category(Field):
    extended_name: str
    hard_skills: List[HardSkill]

    def __init__(self, name, extended_name, required=False):
        super().__init__(name, required)
        self.name = name
        self.extended_name = extended_name


class SoftSkill(Field):
    pass

class UpdateSetList:
    @staticmethod
    def update_set(right: set[Field], left: list[Field]):
        right.update(tuple(left))
        return right

class State(TypedDict):
    id: str
    data_estrazione: str
    data: str
    name: str
    company: str
    company_sector: str #AI
    company_revenue: str #AI
    company_registered_office_state: str #AI
    work_mode: str
    work_type: str
    experience: str
    city: str
    region: str
    state:  str
    macro_region: str
    job_sector: str
    job_area: str
    qualification: str
    announce: str
    ral: int #AI
    summarized_announce: str #AI
    categories: Annotated[set[Category], UpdateSetList.update_set] #AI
    soft_skills: Annotated[set[SoftSkill], UpdateSetList.update_set] #AI
