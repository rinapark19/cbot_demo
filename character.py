import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, TransformChain, SequentialChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
import json


def get_memory(): # 대화 기록을 저장하는 메모리
    memory = ConversationBufferMemory(memory_key="chat_history", ai_prefix="bot", human_prefix="you")
    return memory

def get_search_chain(intro, story, line): # 인격을 지정하기 위해 데이터를 가져오는 코드
    def get_data(input_variables):
        chat = input_variables["chat"]
        return {"intro": intro, "story": story, "line": line}
    
    search_chain = TransformChain(input_variables=["chat"], output_variables=["intro", "story", "line"], transform=get_data)
    return search_chain

def get_current_memory_chain(): # 현재 대화 기록을 가져오는 코드
    def transform_memory_func(input_variables):
        current_chat_history = input_variables["chat_history"].split("\n")[-10:]
        current_chat_history = "\n".join(current_chat_history)
        return{"current_chat_history": current_chat_history}
    
    current_memory_chain = TransformChain(input_variables=["chat_history"], output_variables=["current_chat_history"], transform=transform_memory_func)
    return current_memory_chain

def get_chatgpt_chain(): # GPT-4를 사용하여 대화를 생성하는 코드
    llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"])
    
    template = """ 너는 'You'가 말을 했을 때 'bot'이 대답하는 것처럼 대화를 해 줘.
    
    'bot'은 대체적으로 이런 인물이야. 이 문서를 참고하면 돼. {intro}
    'bot'의 캐릭터 소개, 성격, 인물 배경, 작중 행적 등은 이 문서를 참고해. {story}
    'bot' 대사의 예시를 보여 줄 테니까, 'bot'의 말과 습관, 생각을 잘 유추해 봐
    Examples: {line}
    
    위에서 참고한 각 문서를 읽고 나서, 'bot'의 말투와 성격을 잘 따라해 줘.
    다음 대화에서 'bot'이 할 것 같은 답변을 해 봐.
    1. 'bot'의 스타일대로, 'bot'이 할 것 같은 말을 해야 해.
    2. 자연스럽게 'bot'의 말투와 성격을 따라해야 해. 번역한 것 같은 말투 쓰지 마.
    3. 'You'의 말을 이어서 만들지 말고 'bot' 말만 결과로 줘.
    4. 다섯 문장 이내로 짧게 대답하되, 'You'와 대화가 이어질 수 있도록 자연스럽게 말해 줘.
    5. 'bot'의 성격, 인물 배경, 작중 행적 등의 설정을 제대로 반영해 줘. 없는 말 지어내지 마. 
    
    이전 대화:
    {current_chat_history}
    You: {chat}
    bot: 
    """
    
    prompt_template = PromptTemplate(input_variables=["chat", "current_chat_history", "intro", "story", "line"], template=template)
    chatgpt_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="received_chat")
    
    return chatgpt_chain

class OverallChain:
    def __init__(self, intro, story, line) -> None:
        self.memory = get_memory()
        self.search_chain = get_search_chain(intro, story, line)
        self.current_memory_chain = get_current_memory_chain()
        self.chatgpt_chain = get_chatgpt_chain()
        
        self.overall_chain = SequentialChain(
            memory=self.memory,
            chains=[self.search_chain, self.current_memory_chain, self.chatgpt_chain],
            input_variables=["chat"],
            output_variables=["received_chat"],
            verbose=True
        )
    
    def receive_chat(self, chat):
        review = self.overall_chain.invoke({"chat": chat})
        return review['received_chat']