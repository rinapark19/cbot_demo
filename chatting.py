from situation import Character
from character import OverallChain
import streamlit as st
import os
import json

def display_chat_message(profile_image_url, message):
    st.markdown(
        f'<div style="display: flex; align-items: center;">'
        f'<img src="{profile_image_url}" style="border-radius: 50%; width: 30px; height: 30px; margin-right: 10px;">'
        f'{message}'
        f'</div><br>',
        unsafe_allow_html=True
    )

def character_page(intro, story, line, situations, sit_line, bot_profile, user_profile, isSit):
    if isSit:
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": sit_line, "profile_image_url": bot_profile}]
        elif len(st.session_state.messages) == 1:
            st.session_state.messages = [{"role": "assistant", "content": sit_line, "profile_image_url": bot_profile}]
        
        for message in st.session_state.messages:
            display_chat_message(message["profile_image_url"], message["content"])
            
        chatbot = Character(intro, story, line, situations)
            
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt, "profile_image_url": user_profile})
            display_chat_message(user_profile, prompt)
            
            assistant_response = chatbot.receive_chat(prompt)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response, "profile_image_url": bot_profile})
            display_chat_message(bot_profile, assistant_response)
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        elif len(st.session_state.messages) == 1:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            display_chat_message(message["profile_image_url"], message["content"])
            
        chatbot = OverallChain(intro, story, line)
            
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt, "profile_image_url": user_profile})
            display_chat_message(user_profile, prompt)
            
            assistant_response = chatbot.receive_chat(prompt)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response, "profile_image_url": bot_profile})
            display_chat_message(bot_profile, assistant_response)
       

def main():
    os.environ["OPENAI_API_KEY"] = st.secrets["openai_key"]
    
    st.title("웹툰 챗봇🤖")
    st.info("네이버웹툰 캐릭터를 선택하고, 그냥 대화하거나 상황을 선택하여 대화를 나눌 수 있습니다. 우측 상단 > 를 클릭해 캐릭터를 선택하세요.")
    
    st.sidebar.title("캐릭터 및 상황 선택")
    
    with open("sit_data/chars.json", "r", encoding="utf-8") as f:
        json_data = f.read()
    
    chars = json.loads(json_data)
    bots = [entry["bot"] for entry in chars]
    bots.insert(0, "선택")
    
    selected_char = st.sidebar.selectbox(
        "대화할 캐릭터를 선택하세요.",
        bots,
    )
    
    if selected_char != "선택":
        bot_data = next((entry for entry in chars if entry["bot"] == selected_char), None)
        situations = bot_data["situations"]
        bot_profile = bot_data["profile"]
        sit_titles = [entry["sit_title"] for entry in situations]
        sit_titles.insert(0, "상황 없이 대화하기")
        
        selected_sit = st.sidebar.radio(
            "대화할 상황을 선택하세요.",
            sit_titles,
        )
        
        if selected_sit == "상황 없이 대화하기":
            intro = bot_data["intro"]
            story = bot_data["story"]
            line = bot_data["line"]
            situations = bot_data
            user_profile = "https://cdn1.iconfinder.com/data/icons/freeline/32/account_friend_human_man_member_person_profile_user_users-512.png"
            
            if "bot" not in st.session_state: # 처음 할 때
                st.session_state.bot = selected_char
            elif st.session_state.bot != selected_char: # 캐릭터 바꿀 때
                st.session_state.clear()
                
            if "sit" not in st.session_state:
                st.session_state.sit = selected_sit
            elif st.session_state.sit != selected_sit:
                st.session_state.clear()
            character_page(intro, story, line, None, "", bot_profile, user_profile, False)
        
        
        if selected_sit != "상황 없이 대화하기":
            sit_data = next((entry for entry in situations if entry["sit_title"] == selected_sit), None)
            sit_line = sit_data["sit_line"]
            user_profile = sit_data["sit_profile"]
            
            intro = bot_data["intro"]
            story = bot_data["story"]
            line = bot_data["line"]
            situations = sit_data
            
            if "bot" not in st.session_state: # 처음 할 때
                st.session_state.bot = selected_char
            elif st.session_state.bot != selected_char: # 캐릭터 바꿀 때
                st.session_state.clear()
            
            if "sit" not in st.session_state:
                st.session_state.sit = selected_sit
            elif st.session_state.sit != selected_sit:
                st.session_state.clear()
            
            character_page(intro, story, line, situations, sit_line, bot_profile, user_profile, True)

if __name__ == "__main__":
    main()
            
        
    
    
        