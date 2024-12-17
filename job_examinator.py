import operator
from typing import Annotated, Any


from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

from agents import job_preprocess_agent, check_category_agent, hard_skill_match_agent
from model import Category, SoftSkill, HardSkill, job_sectors


class State(TypedDict):
    name: str
    company: str
    type: Literal['junior', 'mid-level', 'senior']
    city: str
    region: str
    state:  str
    contract_type: Literal['stage', 'determinato', 'indeterminato']
    announce: str
    summarized_announce: str
    categories: Annotated[list[Category], operator.add]
    soft_skill: list[SoftSkill]


# Nodo di ingresso
def preprocess_level(state: State) -> State:
    """Nodo iniziale che processa lo stato in ingresso e apporta le modifiche comuni a tutte le categorie"""

    agent = job_preprocess_agent()

    result = agent.invoke({"job_posting": state['announce']})

    state['type'] = result["contract_info"][0]
    state['contract_type'] = result["contract_info"][1]
    state['summarized_announce'] = result["skills"]

    print("Contratto e Livello:", result["contract_info"])
    print("\nSkill richieste:\n", result["skills"])


    return state


def check_category(state: State, category: str) -> State:
    agent = check_category_agent()

    category_dict = job_sectors[category]

    required = agent.invoke({
        "category": category_dict[0],
        "category_description": category_dict[1],
        "job_posting": state['announce']
    })

    category = Category(category, category_dict[0], required=required)
    state['categories'].append(category)

    return State

def check_hard_skill(state: State, category_name: str) -> State:

    category_dict = job_sectors[category_name]
    categories = state['categories']
    category = next(ca for ca in categories if ca.extended_name == category_name)

    hard_skill_agent = hard_skill_match_agent()
    hard_skill_matched = hard_skill_agent.invoke({
            "job_description": state['summarized_announce'],
            "skills": ", ".join(category_dict[2])
        })

    hard_skills = list[HardSkill]

    for hs in category_dict[2]:
        hard_skill = HardSkill()
        hard_skill.name = hs
        hard_skill.required = hs in hard_skill_matched
        hard_skills.append(hard_skill)

    category.hard_skills = hard_skills

    return State


def check_soft_skill(state: State) -> State:

    #TODO IMPLEMENTARE AGENTE
    
    soft_skill: list[SoftSkill] = []
    state['soft_skill'] = soft_skill

    return State

def should_check_hard_skill(state: State, category_name: str) -> str:

    categories = state['categories']
    category: Category = next(ca for ca in categories if ca.extended_name == category_name)

    if category.required:
        return f'check_hard_skill_{category}'

    return END

def get_graph() -> CompiledStateGraph:

    builder = StateGraph(State)
    
    #CREAZIONE DEI NODI
    
    builder.add_node("preprocess_level", preprocess_level)
    
    builder.add_node("check_soft_skill", check_soft_skill)
    
    builder.add_node("check_category_sistemi", lambda s: check_category(s, 'sistemi'))
    builder.add_node("check_category_database", lambda s: check_category(s, 'database'))
    builder.add_node("check_category_management", lambda s: check_category(s, 'management'))
    builder.add_node("check_category_ux_designer", lambda s: check_category(s, 'ux_designer'))
    builder.add_node("check_category_data_science", lambda s: check_category(s, 'data_science'))
    builder.add_node("check_category_sviluppo_software", lambda s: check_category(s, 'sviluppo_software'))

    builder.add_node("check_hard_skill_sistemi", lambda s: check_hard_skill(s, 'sistemi'))
    builder.add_node("check_hard_skill_database", lambda s: check_hard_skill(s, 'database'))
    builder.add_node("check_hard_skill_management", lambda s: check_hard_skill(s, 'management'))
    builder.add_node("check_hard_skill_ux_designer", lambda s: check_hard_skill(s, 'ux_designer'))
    builder.add_node("check_hard_skill_data_science", lambda s: check_hard_skill(s, 'data_science'))
    builder.add_node("check_hard_skill_sviluppo_software", lambda s: check_hard_skill(s, 'sviluppo_software'))

    #CREAZIONE DEI COLLEGAMENTI
    
    builder.add_edge(START, "preprocess_level")

    builder.add_edge('preprocess_level', 'check_soft_skill')
    builder.add_edge("check_soft_skill", END)

    builder.add_edge('preprocess_level', 'check_category_sistemi')
    builder.add_edge('preprocess_level', 'check_category_database')
    builder.add_edge('preprocess_level', 'check_category_management')
    builder.add_edge('preprocess_level', 'check_category_ux_designer')
    builder.add_edge('preprocess_level', 'check_category_data_science')
    builder.add_edge('preprocess_level', 'check_category_sviluppo_software')

    builder.add_conditional_edges('check_category_sistemi', lambda s: should_check_hard_skill(s, 'sistemi'))
    builder.add_conditional_edges('check_category_database', lambda s: should_check_hard_skill(s, 'database'))
    builder.add_conditional_edges('check_category_management', lambda s: should_check_hard_skill(s, 'management'))
    builder.add_conditional_edges('check_category_ux_designer', lambda s: should_check_hard_skill(s, 'ux_designer'))
    builder.add_conditional_edges('check_category_data_science', lambda s: should_check_hard_skill(s, 'data_science'))
    builder.add_conditional_edges('check_category_sviluppo_software', lambda s: should_check_hard_skill(s, 'sviluppo_software'))
    
    builder.add_edge("check_hard_skill_sistemi", END)
    builder.add_edge("check_hard_skill_database", END)
    builder.add_edge("check_hard_skill_management", END)
    builder.add_edge("check_hard_skill_ux_designer", END)
    builder.add_edge("check_hard_skill_data_science", END)
    builder.add_edge("check_hard_skill_sviluppo_software", END)

    return builder.compile()