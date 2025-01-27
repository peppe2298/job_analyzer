from io import BytesIO

from PIL import Image
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.constants import END, START
from langgraph.graph.state import CompiledStateGraph, StateGraph

from model.graph.state import State
from service.graph_service import GraphService


class JobAnalyzerGraph:
    def __init__(self):
        self.gs = GraphService()
        self.graph: CompiledStateGraph = self.generate_graph()

    def generate_image(self) -> Image:
        image_data = BytesIO(self.graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API))
        image = Image.open(image_data)
        return image

    def generate_graph(self):
        builder = StateGraph(State)

        # CREAZIONE DEI NODI

        builder.add_node("check_company", self.gs.check_company)
        builder.add_node("check_date", self.gs.check_date)

        builder.add_node("preprocess_level", self.gs.preprocess_job)
        builder.add_node("check_soft_skill", self.gs.check_soft_skill)

        builder.add_node("check_category_sistemi", lambda s: self.gs.check_category(s, 'sistemi'))
        builder.add_node("check_category_database", lambda s: self.gs.check_category(s, 'database'))
        builder.add_node("check_category_management", lambda s: self.gs.check_category(s, 'management'))
        builder.add_node("check_category_ux_designer", lambda s: self.gs.check_category(s, 'ux_designer'))
        builder.add_node("check_category_data_science", lambda s: self.gs.check_category(s, 'data_science'))
        builder.add_node("check_category_sviluppo_software", lambda s: self.gs.check_category(s, 'sviluppo_software'))

        builder.add_node("check_hard_skill_sistemi", lambda s: self.gs.check_hard_skill(s, 'sistemi'))
        builder.add_node("check_hard_skill_database", lambda s: self.gs.check_hard_skill(s, 'database'))
        builder.add_node("check_hard_skill_management", lambda s: self.gs.check_hard_skill(s, 'management'))
        builder.add_node("check_hard_skill_ux_designer", lambda s: self.gs.check_hard_skill(s, 'ux_designer'))
        builder.add_node("check_hard_skill_data_science", lambda s: self.gs.check_hard_skill(s, 'data_science'))
        builder.add_node("check_hard_skill_sviluppo_software", lambda s: self.gs.check_hard_skill(s, 'sviluppo_software'))

        # CREAZIONE DEI COLLEGAMENTI

        builder.add_edge(START, 'check_company')
        builder.add_edge("check_company", END)

        builder.add_edge(START, 'check_date')
        builder.add_edge("check_date", END)

        builder.add_edge(START, "preprocess_level")

        builder.add_edge('preprocess_level', 'check_soft_skill')
        builder.add_edge("check_soft_skill", END)

        builder.add_edge('preprocess_level', 'check_category_sistemi')
        builder.add_edge('preprocess_level', 'check_category_database')
        builder.add_edge('preprocess_level', 'check_category_management')
        builder.add_edge('preprocess_level', 'check_category_ux_designer')
        builder.add_edge('preprocess_level', 'check_category_data_science')
        builder.add_edge('preprocess_level', 'check_category_sviluppo_software')


        # AGGIUNTA DEI COLLEGAMENTI CONDIZIONALI

        builder.add_conditional_edges('check_category_sistemi', lambda s: self.gs.should_check_hard_skill(s, 'sistemi'),
                                      path_map=["check_hard_skill_sistemi", END])
        builder.add_conditional_edges('check_category_database', lambda s: self.gs.should_check_hard_skill(s, 'database'),
                                      path_map=["check_hard_skill_database", END])
        builder.add_conditional_edges('check_category_management', lambda s: self.gs.should_check_hard_skill(s, 'management'),
                                      path_map=["check_hard_skill_management", END])
        builder.add_conditional_edges('check_category_ux_designer', lambda s: self.gs.should_check_hard_skill(s, 'ux_designer'),
                                      path_map=["check_hard_skill_ux_designer", END])
        builder.add_conditional_edges('check_category_data_science',
                                      lambda s: self.gs.should_check_hard_skill(s, 'data_science'),
                                      path_map=["check_hard_skill_data_science", END])
        builder.add_conditional_edges('check_category_sviluppo_software',
                                      lambda s: self.gs.should_check_hard_skill(s, 'sviluppo_software'),
                                      path_map=["check_hard_skill_sviluppo_software", END])

        builder.add_edge("check_hard_skill_sistemi", END)
        builder.add_edge("check_hard_skill_database", END)
        builder.add_edge("check_hard_skill_management", END)
        builder.add_edge("check_hard_skill_ux_designer", END)
        builder.add_edge("check_hard_skill_data_science", END)
        builder.add_edge("check_hard_skill_sviluppo_software", END)

        return builder.compile()

