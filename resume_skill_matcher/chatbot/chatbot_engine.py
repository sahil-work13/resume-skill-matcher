import requests

class CloudLlamaBot:
    def __init__(self, api_url, system_prompt):
        self.api_url = api_url
        self.system_prompt = system_prompt

    def run(self, user_input):
        payload = {
            "prompt": user_input,
            "system_prompt": self.system_prompt
        }

        response = requests.post(self.api_url, json=payload, timeout=60)
        response.raise_for_status()

        return response.json()["answer"]


def get_chatbot(resume_context, jd_context=None):
    system_prompt = (
        "You are a professional Resume & Career Assistant.\n\n"
        f"{resume_context}"
    )

    return CloudLlamaBot(
        api_url="https://sk1354/llama3-career-api.hf.space/chat",
        system_prompt=system_prompt
    )
