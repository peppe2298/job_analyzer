from langgraph.constants import END

from model.agents.abstract.abstract_agent import AbstractAgent
from model.agents.company.company_agent import CompanyAgent, ProcessedCompanies, Company
from model.agents.job.check_job_agent import CheckCategoryAgent, CheckSkillAgent, DateAgent
from model.agents.job.job_preprocess_agent import JobPreprocessAgent
from model.graph.state import State, Category, HardSkill, SoftSkill
from model.job_info import job_sectors, job_soft_skills
from model.prompts import check_category_prompt, hard_skill_match, soft_skill_match


class GraphService:
    @staticmethod
    def should_check_hard_skill(state: State, category_name: str) -> str:
        categories = state['categories']
        category: Category = next(ca for ca in categories if ca.name == category_name)

        if category.required:
            return f'check_hard_skill_{category_name}'

        return END

    @staticmethod
    def check_category(state: State, category: str):
        agent = CheckCategoryAgent(prompt = check_category_prompt)

        category_dict = job_sectors[category]

        required = agent.invoke({
            "category": category_dict[0],
            "category_description": category_dict[1],
            "job_posting": state['announce']
        })

        category = Category(category, category_dict[0], required=required)
        category.hard_skills = []

        return {'categories': [category]}

    @staticmethod
    def check_hard_skill(state: State, category_name: str):

        category_dict = job_sectors[category_name]
        categories = state['categories']
        category = next(ca for ca in categories if ca.name == category_name)

        hard_skill_agent = CheckSkillAgent(prompt=hard_skill_match)

        hard_skill_matched = hard_skill_agent.invoke({
            "job_description": state['summarized_announce'],
            "skills": ", ".join(category_dict[2])
        })

        hard_skills: list[HardSkill] = []

        for hs in category_dict[2]:
            hard_skill = HardSkill(name=hs)
            hard_skill.required = hs in hard_skill_matched
            hard_skills.append(hard_skill)

        category.hard_skills = hard_skills

        return {'categories': [category]}

    @staticmethod
    def check_soft_skill(state: State):

        soft_skill_agent = CheckSkillAgent(prompt=soft_skill_match)
        soft_skill_matched = soft_skill_agent.invoke({
            "job_description": state['summarized_announce'],
            "skills": ", ".join(job_soft_skills)
        })

        soft_skills: list[SoftSkill] = []

        for soft_skill_name in job_soft_skills:
            soft_skill = SoftSkill(soft_skill_name)
            soft_skill.required = soft_skill_name in soft_skill_matched
            soft_skills.append(soft_skill)

        return {'soft_skills': soft_skills}

    @staticmethod
    def preprocess_job(state: State):
        """Nodo iniziale che processa lo stato in ingresso e apporta le modifiche comuni a tutte le categorie"""

        agent =  JobPreprocessAgent()
        result = agent.invoke({'job_posting': state['announce']})

        return {'summarized_announce':  result["skills"], 'ral': result["ral"]}

    @staticmethod
    def check_company(state: State):

        processed_companies = ProcessedCompanies()
        company_name = state['company']

        if company_name in processed_companies.get_data():
            company = processed_companies.get_data().get(company_name)
            return {'company_registered_office_state': company.country, 'company_sector': company.sector,
                'company_revenue': company.revenue}

        agent = CompanyAgent()
        results = agent.invoke({'company_name': state['company']})
        company = Company(country=results['country']['output'], revenue=results['revenue']['output'], sector=results['sector']['output'])
        processed_companies.update_data(company_name, company)
        print(company.country)
        return {'company_registered_office_state': company.country, 'company_sector': company.sector,
                'company_revenue': company.revenue}

    @staticmethod
    def check_date(state: State):

        unformatted_date = state['data']
        extraction_date = state['data_estrazione']

        agent = DateAgent()
        result = agent.invoke({'extraction_date': extraction_date, 'unformatted_date': unformatted_date})

        return {'data': result}