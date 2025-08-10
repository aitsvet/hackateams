import json
import pandas as pd

from langchain_community.llms import Ollama
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from model import Participant

with open('messages.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

llm = Ollama(model="gpt-oss:20b", temperature=0.0)
parser = PydanticOutputParser(pydantic_object=Participant)
prompt = PromptTemplate(
    template="""Извлеки информацию об участнике из следующего текста.

Текст: {input}

{format_instructions}

В ответе обязательно переведи все термины на русский и расшифруй все аббревиатуры, кроме HR, AI, GPT и названий языков программирования и программных средств.

ВАЖНО: Ответ должен содержать ТОЛЬКО JSON в указанном формате без дополнительных комментариев или пояснений.""",
    input_variables=["input"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

patricipants = []
patricipants_dict = []
for idx, item in enumerate(data):
    print(f"Обработка элемента {idx+1}/{len(data)}")
    try:
        chain = prompt | llm | parser
        Participant = chain.invoke({"input": str(item)})
        print(Participant)
        patricipants.append(Participant)
    except Exception as e:
        print(f"Ошибка при обработке элемента {idx}: {str(e)}")
        continue
    patricipants_dict.append({
        "id": Participant.id,
        "name": Participant.name,
        "location": Participant.location,
        "availability": Participant.availability,
        "roles": "\n".join(Participant.roles) if Participant.roles else None,
        "skills": "\n".join(Participant.skills) if Participant.skills else None,
        "having": "\n".join(Participant.having) if Participant.having else None,
        "looking_for": "\n".join(Participant.looking_for) if Participant.looking_for else None,
        "experience": "\n".join(Participant.experience) if Participant.experience else None,
        "interests": "\n".join(Participant.interests) if Participant.interests else None,
        "idea": Participant.idea
    })

with open('participants.json', 'w', encoding='utf-8') as f:
    f.write('[\n' + ',\n'.join(map(lambda r: r.model_dump_json(), patricipants)) + '\n]')

df = pd.DataFrame(patricipants_dict)
df.to_excel("participants.xlsx", index=False, engine='openpyxl')