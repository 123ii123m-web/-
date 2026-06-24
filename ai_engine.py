Claude:
ai_engine.py

```python
import asyncio
import logging
import re
from openai import AsyncOpenAI

from config import Config

logger = logging.getLogger(name)

class AIEngine:
    """موتور ۳ هوش مصنوعی — اجرای همزمان و تلفیق بهترین نتیجه"""

    def init(self):
        self.clients = {}

        if Config.OPENAI_API_KEY:
            self.clients["openai"] = {
                "client": AsyncOpenAI(api_key=Config.OPENAI_API_KEY),
                "model": Config.OPENAI_MODEL,
            }
        if Config.DEEPSEEK_API_KEY:
            self.clients["deepseek"] = {
                "client": AsyncOpenAI(
                    api_key=Config.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com",
                ),
                "model": Config.DEEPSEEK_MODEL,
            }
        if Config.GROQ_API_KEY:
            self.clients["groq"] = {
                "client": AsyncOpenAI(
                    api_key=Config.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                ),
                "model": Config.GROQ_MODEL,
            }

        if not self.clients:
            raise ValueError("حداقل یک API Key باید تنظیم بشه!")

        logger.info(f"AI Engine loaded with: {', '.join(self.clients.keys())}")

    async def _call_model(
        self, name: str, client: AsyncOpenAI, model: str, prompt: str
    ) -> str | None:
        """فراخوانی یک مدل — با timeout و هندل خطا"""
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "تو یک برنامه‌نویس حرفه‌ای پایتونی. "
                            "فقط کد تمیز و قابل اجرا تحویل بده. "
                            "هیچ توضیح اضافه نده."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
                timeout=120,
            )
            content = resp.choices[0].message.content
            logger.info(f"{name}: پاسخ دریافت شد ({len(content)} کاراکتر)")
            return content
        except Exception as e:
            logger.error(f"{name} failed: {e}")
            return None

    async def _merge_responses(
        self, prompt: str, responses: dict[str, str | None]
    ) -> str:
        """تلفیق پاسخ‌ها — از قوی‌ترین مدل موجود برای ترکیب استفاده می‌کنه"""
        successful = {k: v for k, v in responses.items() if v}
        if not successful:
            raise RuntimeError("همه مدل‌ها خطا دادن!")

        if len(successful) == 1:
            name, code = list(successful.items())[0]
            logger.info(f"Only {name} responded, using directly")
            return self._extract_code(code)

        merge_prompt = (
            "You are a senior code reviewer. Three AI models generated Python code "
            "for the same task.\n"
            "Review ALL three outputs below. Pick the best parts from each, "
            "fix any bugs, merge them into one FINAL clean working version.\n"
            "Only output the final code, no explanations.\n\n"
            f"Task:\n{prompt}\n\n"
        )
        for name, code in successful.items():
            merge_prompt += f"\n--- {name.upper()} output ---\n{code}\n"

        merge_prompt += "\n\n--- FINAL MERGED CODE ---\n"

اولویت با OpenAI برای تلفیق
        if "openai" in self.clients:
            merger = self.clients["openai"]
        else:
            merger = self.clients[list(self.clients.keys())[0]]

        try:
            resp = await merger["client"].chat.completions.create(
                model=merger["model"],
                messages=[{"role": "user", "content": merge_prompt}],
                temperature=0.2,
                max_tokens=4000,
                timeout=120,
            )
            merged = resp.choices[0].message.content
            logger.info(f"Merged result: {len(merged)} chars")
            return self._extract_code(merged)
        except Exception as e:
            logger.warning(f"Merge failed: {e}, using first response")
            return self._extract_code(list(successful.values())[0])

    def _extract_code(self, text: str) -> str:
        """استخراج کد از بلاک مارک‌داون — توی  یا """
        match = re.search(r"(?:python)?\n(.*?)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        match = re.search(r"\n(.*?)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def generate_code(self, prompt: str) -> str:
        """
        تولید کد با هر ۳ مدل همزمان — تلفیق و برگردوندن بهترین خروجی
        """
        logger.info(f"Generating code for: {prompt[:100]}...")

        tasks = {}
        for name, cfg in self.clients.items():
            tasks[name] = self._call_model(
                name, cfg["client"], cfg["model"], prompt
            )

        results = await asyncio.gather(*tasks.values())
        responses = dict(zip(tasks.keys(), results))

        final_code = await self._merge_responses(prompt, responses)
        return final_code
```
