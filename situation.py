import os
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, TransformChain, SequentialChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma


def get_memory(): # 대화 기록을 저장하는 메모리
    memory = ConversationBufferMemory(memory_key="chat_history", ai_prefix="bot", human_prefix="you")
    return memory

def get_search_chain(intro, story, line, situations): # 인격을 지정하기 위해 데이터를 가져오는 코드
    def get_data(input_variables):
        chat = input_variables["chat"]
        
        situation = situations["situation"]
        relation = situations["relation"]
        
        
        return {"intro": intro, "story": story, "line": line, "situation": situation, "relation": relation}
    
    search_chain = TransformChain(input_variables=["chat"], output_variables=["intro", "story", "line", "situation", "relation"], transform=get_data)
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
    
    template = """ 너는 'User'가 말을 했을 때, 'Bot'이 상황에 맞춰서 대답하는 것처럼 대화를 해 줘.
    'Bot'은 대체적으로 이런 인물이야. {intro}
    'Bot'의 이야기는 이렇게 되어 있어. 이걸 통해 성격이나 행동을 유추해 봐. {story}
    'Bot'의 대사의 예시를 보여 줄 테니까, 'Bot'의 말과 습관, 생각을 잘 유추해 봐. {line}
    
    'User'와의 관계는 이래. {relation}
    'User'와 'Bot'은 현재 이런 상황에서 대화를 나누고 있어. {situation}
    
    위에서 참고한 각 문서를 읽고 나서, 'Bot'의 말투와 성격을 따라해서 상황에 맞춰서 이야기를 진행해 줘.
    다음 대화에서 'Bot'이 할 것 같은 답변을 해 봐.
    1. 'Bot'의 스타일대로, 'Bot'이 이 상황에서 할 것 같은 말을 해야 해.
    2. 자연스럽게 'Bot'의 말투와 성격을 따라해야 해. 번역한 것 같은 말투를 사용하지 마.
    3. 다섯 문장 이내로 짧게 대답하되, 'User'와 대화가 이어지도록, 상황에 맞춰서 이야기가 진행되도록 해 줘.
    4. 주어진 상황에 맞춰서 'User'한테 할 만한 말을 해 줘. 문서를 참고해서 상황을 제대로 이해하도록 해.
    5. 'User'의 말을 따라하지 마. 'Bot'의 말을 해 줘.
    6. 'Bot'의 캐릭터 이름을 직접적으로 언급하거나, 'Bot:'이라고 표시하지 마. 'Bot'이 할 말만 해 줘.
    
    이전 대화:
    {current_chat_history}
    User: {chat}
    Bot: 
    """
    
    prompt_template = PromptTemplate(input_variables=["chat", "current_chat_history", "intro", "story", "line", "relation", "situation"], template=template)
    chatgpt_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="received_chat")
    
    return chatgpt_chain

class Character:
    def __init__(self, intro, story, line, situations) -> None:
        self.memory = get_memory()
        self.search_chain = get_search_chain(intro, story, line, situations)
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