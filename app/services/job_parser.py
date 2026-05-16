import json
import logging

from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """你是一名中文招聘数据提取专家。从以下招聘信息中提取结构化信息。
以 JSON 格式返回以下字段：
- company_name: string（公司名称，如果未提供则用 null）
- position: string（职位名称）
- salary_range: string（薪资范围，如"25K-50K"）
- requirements_skills: string[]（技能要求列表，每一项是一个具体技能）
- responsibilities: string[]（岗位职责列表）
- education_requirements: string（学历要求）
- experience_requirements: string（经验要求）
- preferred_qualifications: string[]（加分项列表）
- industry: string（所属行业，如果未提供则用 null）

重要规则：
1. 如果文本中未找到某个字段，使用 null 或空数组
2. 技能要求要尽量拆分为单个技能项，不要合并
3. 返回纯净的 JSON，不要包含其他文字"""


class JobParser:
    def __init__(self, ai_service: AIService):
        self.ai = ai_service

    def parse(self, job_text: str) -> dict:
        default = {
            "company_name": None,
            "position": "",
            "salary_range": None,
            "requirements_skills": [],
            "responsibilities": [],
            "education_requirements": None,
            "experience_requirements": None,
            "preferred_qualifications": [],
            "industry": None,
        }

        for attempt in range(2):
            try:
                result = self.ai.extract_structured(EXTRACTION_PROMPT, job_text)
                merged = {**default, **result}
                return merged
            except Exception as e:
                logger.warning(f"Job parsing attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    raise RuntimeError("招聘信息解析失败，请检查文本是否完整或尝试重新提交")

        return default
