from langchain_core.prompts import ChatPromptTemplate

# Prompt per l'estrazione delle skill non catalogate
skills_prompt = ChatPromptTemplate.from_template("""
Analyze the following job posting and keep only the parts related to the requested soft and hard skills.
Remove all other irrelevant information such as company benefits, company description, etc.
Keep the original formatting of the skills.

Job posting:
{job_posting}
""")

check_category_prompt = ChatPromptTemplate.from_template("""

Analyze whether the indicators specified in the criteria are present in the job posting.

Respond ONLY with:
- True: if the Job posting contains the indicators of the industry
- False: if the Job posting does not contain the indicators of the industry

Industry to check: {category}
Criteria to identify the industry (indicators to look for in the Job posting): {category_description}

Job posting text to analyze:
{job_posting}

""")

hard_skill_match = ChatPromptTemplate.from_template("""
Review the following job posting and identify which of the skills provided are required.
IMPORTANT: If you find a required skill that has a different name but refers to the same technology as the list provided,
you must return the EXACT name from the input list.

For example:
- If the list says "React.js" and the posting says "React" or "ReactJS", return "React.js"
- If the list says "MySQL" and the posting says "SQL", return "MySQL" only if it is clear that it refers specifically to MySQL

Return ONLY the required skills, one per line.
If a skill is not mentioned or is not clearly required, do not include it.

Job Posting:
{job_description}

List of skills to verify (use EXACTLY these names):
{skills}

Required skills (one per line):
""")

soft_skill_match = ChatPromptTemplate.from_template("""
Review the following job posting and identify which of the provided soft skills are required.
IMPORTANT: If you find a required skill that has a different name but refers to the same technology as the list provided,
you must return the EXACT name from the input list.

For example:
- If the list says "Leadership and Influence" and the posting says "Ability to influence others" or "possession of leadership", return "React.js"
- If the list says "Team Collaboration and Teamwork" and the posting says "Ability to work in a team", return "Team Collaboration and Teamwork"

Return ONLY the required skills, one per line.
If a skill is not clearly required, do not include it.

Job Posting:
{job_description}

List of soft skills to verify (use EXACTLY these names):
{skills}

Required skills (one per line):
""")

ral_prompt = ChatPromptTemplate.from_template("""
Given the following job posting, calculate the RAL (Gross Annual Salary) following these rules:
1. **Range of values**: If there is a range (example: "25,000-30,000€"), calculate the average and return an integer.
2. **Single value**: If a single value is given (example: "35,000€"), return that value as an integer.
3. **Monthly salary**: If there is a monthly salary (example: "1,500€ per month"), calculate the RAL by multiplying by 14 (14 monthly payments) and return the result as an integer.
4. **No value**: If there is no indication of RAL or salary, return `0`.

Make sure the output is **just an integer**, without additional explanations.

**Examples**:
1. Input: "Company X is looking for a Data Scientist. We offer a salary between €25,000 and €30,000 based on experience."
Output: 27500
2. Input: "Company Y is looking for a Web Developer with a monthly salary of €1,800."
Output: 25200
3. Input: "Company Z is looking for a Project Manager. Excellent growth prospects."
Output: 0

**Job posting**: {job_posting}

**Result**:
"""
)