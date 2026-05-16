import json
import logging

from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

OPTIMIZE_PROMPT = """你是一名专业的中文简历写作专家和职业规划师。你的任务是根据目标职位的要求优化用户的简历。

严格规则：
1. 不得编造经历、技能或资质——所有事实信息必须保持准确
2. 重新措辞现有经历，突出与职位描述相关的关键词
3. 重新排列技能列表，优先展示与需求匹配的技能
4. 使用积极主动的语言，尽量使用可量化的成就（数字、百分比等）
5. 输出必须是有效的 JSON 格式

目标职位：{position} @ {company_name}
关键要求：{requirements}

用户原始简历：
{resume_text}

请返回以下 JSON 格式：
{{
  "optimized_text": "优化后的完整简历文本，从个人信息开始到结束，包含个人简介、工作经历、项目经验、技能清单、教育背景等章节",
  "matching_score": 0-1之间的数值，代表简历匹配度,
  "improvements": ["改进项1", "改进项2", ...],
  "highlighted_skills": ["与职位高度匹配的技能1", "技能2", ...]
}}"""

GENERATE_PROMPT = """你是一名专业的中文简历写作专家。根据用户的背景信息和目标职位要求，从零生成一份高质量的定制简历。

要求：
1. 基于用户提供的真实背景信息进行扩展和润色
2. 突出与目标职位相关的技能和经验
3. 使用积极主动的专业语言和可量化的成就描述
4. 输出必须是有效的 JSON 格式

目标职位：{position} @ {company_name}
关键要求：{requirements}

用户背景信息：
{background}

请返回以下 JSON 格式：
{{
  "optimized_text": "完整简历文本，包含个人信息、个人简介、工作经历、项目经验、技能清单、教育背景等",
  "matching_score": 0-1之间的数值，代表简历与职位的匹配度,
  "improvements": ["设计亮点1", "设计亮点2", ...],
  "highlighted_skills": ["突出展示的技能1", "技能2", ...]
}}"""

SKILL_GAP_PROMPT = """你是一名职业发展分析师。分析用户的简历内容，提取其中的技能，然后与目标职位的要求进行逐项对比分析。

目标职位：{position} @ {company_name}

职位要求的技能：
{required_skills}

用户简历全文：
{resume_text}

请仔细阅读用户简历，从中提取用户具备的实际技能（编程语言、框架、工具、平台、软技能等），然后与职位要求的技能进行对比。

分类规则：
- "matching": 用户简历中明显具备且符合职位要求的技能
- "gap": 职位要求但用户简历中未体现的技能
- "partial": 用户有相关经验但不完全匹配的技能（如要求Kubernetes但用户只有Docker经验）

学习建议要具体、可操作，针对每个缺失技能给出2-3个具体的学习资源或行动计划。

返回 JSON：
{{
  "matching_skills": [{{"name": "技能名", "proficiency": "熟练程度（如精通/熟练/了解）"}}],
  "gap_skills": [{{"name": "技能名", "required_level": "职位要求的程度"}}],
  "partial_skills": [{{"name": "技能名", "note": "差距说明"}}],
  "recommendations": [
    {{
      "skill": "技能名",
      "priority": "high/medium/low",
      "reason": "为什么需要学习这个技能",
      "resources": ["具体学习建议1（如推荐课程、书籍、实践项目）", "具体学习建议2"]
    }}
  ],
  "overall_match_percentage": 0-100的整数
}}"""


class ResumeOptimizer:
    def __init__(self, ai_service: AIService):
        self.ai = ai_service

    def optimize(self, resume_text: str, job_data: dict) -> dict:
        position = job_data.get("position", "目标职位")
        company = job_data.get("company_name", "目标公司")
        requirements = ", ".join(job_data.get("requirements_skills", []))

        prompt = OPTIMIZE_PROMPT.format(
            position=position,
            company_name=company,
            requirements=requirements or "详见职位描述",
            resume_text=resume_text,
        )

        for attempt in range(2):
            try:
                result = self.ai.extract_structured(
                    "你是一位专业的简历优化专家。请严格按照要求的 JSON 格式输出。",
                    prompt,
                )
                return {
                    "optimized_text": result.get("optimized_text", resume_text),
                    "matching_score": result.get("matching_score", 0.5),
                    "improvements": result.get("improvements", []),
                    "highlighted_skills": result.get("highlighted_skills", []),
                }
            except Exception as e:
                logger.warning(f"Resume optimization attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    raise RuntimeError("简历优化失败，请重试")

        return {"optimized_text": resume_text, "matching_score": 0.5, "improvements": [], "highlighted_skills": []}

    def generate_from_scratch(self, background: str, job_data: dict) -> dict:
        position = job_data.get("position", "目标职位")
        company = job_data.get("company_name", "目标公司")
        requirements = ", ".join(job_data.get("requirements_skills", []))

        prompt = GENERATE_PROMPT.format(
            position=position,
            company_name=company,
            requirements=requirements or "详见职位描述",
            background=background,
        )

        for attempt in range(2):
            try:
                result = self.ai.extract_structured(
                    "你是一位专业的简历生成专家。请严格按照要求的 JSON 格式输出。",
                    prompt,
                )
                return {
                    "optimized_text": result.get("optimized_text", ""),
                    "matching_score": result.get("matching_score", 0.5),
                    "improvements": result.get("improvements", []),
                    "highlighted_skills": result.get("highlighted_skills", []),
                }
            except Exception as e:
                logger.warning(f"Resume generation attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    raise RuntimeError("简历生成失败，请补充更多背景信息后重试")

        return {"optimized_text": "", "matching_score": 0.5, "improvements": [], "highlighted_skills": []}

    def analyze_gaps(self, resume_text: str, job_data: dict) -> dict:
        position = job_data.get("position", "目标职位")
        company = job_data.get("company_name", "目标公司")
        required_skills = json.dumps(job_data.get("requirements_skills", []), ensure_ascii=False)

        prompt = SKILL_GAP_PROMPT.format(
            position=position,
            company_name=company,
            required_skills=required_skills or "（职位描述中未明确列出技能要求）",
            resume_text=resume_text,
        )

        for attempt in range(2):
            try:
                result = self.ai.extract_structured(
                    "你是一位职业发展分析师。请严格按照要求的 JSON 格式输出。",
                    prompt,
                )
                return {
                    "matching_skills": result.get("matching_skills", []),
                    "gap_skills": result.get("gap_skills", []),
                    "partial_skills": result.get("partial_skills", []),
                    "recommendations": result.get("recommendations", []),
                    "overall_match_percentage": result.get("overall_match_percentage", 50),
                }
            except Exception as e:
                logger.warning(f"Skill gap analysis attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    raise RuntimeError("技能分析失败，请重试")

        return {
            "matching_skills": [], "gap_skills": [], "partial_skills": [],
            "recommendations": [], "overall_match_percentage": 50,
        }
