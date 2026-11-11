import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELOS = ["gemini-3.1-flash-lite", "gemini-3-flash-preview"]
PROMPT = "Sugira um prato leve e barato para o almoço."

def gerar(prompt):
    for modelo in MODELOS:
        for tentativa in range(3):
            try:
                resposta = client.models.generate_content(
                    model=modelo, contents=prompt
                )
                return resposta.text
            except errors.ServerError:
                print(f"{modelo} ocupado, tentativa {tentativa + 1}/3...")
                time.sleep(2 * (tentativa + 1))
            except errors.ClientError as e:
                print(f"{modelo} indisponível: {e.code}")
                break
    return "Não foi possível obter resposta agora."

print(gerar(PROMPT))