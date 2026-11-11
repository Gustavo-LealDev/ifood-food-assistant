import json
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODELOS = ["gemini-3.1-flash-lite", "gemini-3-flash-preview"]

with open("cardapio.json", encoding="utf-8") as f:
    CARDAPIO = json.load(f)

INSTRUCAO = f"""Você é o assistente de recomendação de um app de delivery.
Recomende de 1 a 3 pratos SOMENTE do cardápio abaixo. Nunca invente pratos nem preços.
Respeite o orçamento e as restrições alimentares do pedido.
Se nenhum prato servir, devolva lista vazia e explique em "mensagem".
Responda apenas em JSON neste formato:
{{"recomendacoes": [{{"id": 1, "motivo": "..."}}], "mensagem": "..."}}

Cardápio:
{json.dumps(CARDAPIO, ensure_ascii=False)}"""


def chamar_modelo(pedido):
    config = types.GenerateContentConfig(
        system_instruction=INSTRUCAO,
        response_mime_type="application/json",
        temperature=0.3,
    )
    for modelo in MODELOS:
        for tentativa in range(3):
            try:
                resp = client.models.generate_content(
                    model=modelo, contents=pedido, config=config
                )
                return json.loads(resp.text)
            except errors.ServerError:
                time.sleep(2 * (tentativa + 1))
            except (errors.ClientError, json.JSONDecodeError):
                break
    return None


def recomendar(pedido):
    dados = chamar_modelo(pedido)
    if dados is None:
        print("Não consegui responder agora. Tente de novo.")
        return
    por_id = {p["id"]: p for p in CARDAPIO}
    for rec in dados.get("recomendacoes", []):
        prato = por_id.get(rec["id"])
        if prato:
            print(f"- {prato['nome']} (R$ {prato['preco']:.2f}): {rec['motivo']}")
    if dados.get("mensagem"):
        print(dados["mensagem"])


if __name__ == "__main__":
    print("Assistente de comida. Digite 'sair' para encerrar.")
    while True:
        pedido = input("\nO que você quer comer? ")
        if pedido.strip().lower() == "sair":
            break
        recomendar(pedido)