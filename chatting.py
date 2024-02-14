from situation import Character
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

def character_page(intro, story, line, situations, sit_line, bot_profile, user_profile):
    st.title("캐릭터랑 대화하기")
    
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

def main():
    os.environ["OPENAI_API_KEY"] = st.secrets["openai_key"]
    
    st.sidebar.title("캐릭터 선택")
    
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
        sit_titles.insert(0, "선택")
        
        selected_sit = st.sidebar.selectbox(
            "대화할 상황을 선택하세요.",
            sit_titles,
        )
        
        if selected_sit != "선택":
            sit_data = next((entry for entry in situations if entry["sit_title"] == selected_sit), None)
            sit_line = sit_data["sit_line"]
            user_profile = sit_data["sit_profile"]
            
            intro = bot_data["intro"]
            story = bot_data["story"]
            line = bot_data["line"]
            situations = sit_data
            character_page(intro, story, line, situations, sit_line, bot_profile, user_profile)

if __name__ == "__main__":
    main()
            
        
    
    
        