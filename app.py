import streamlit as st
import re
import time
import base64
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------
# [프론트엔드] 앱 기본 설정 및 CSS 디자인
# -------------------------------------------------------------
st.set_page_config(page_title="School-Net Direct", layout="centered", page_icon="🚨")

# 페이지 상태 관리를 위한 세션 초기화 (설명서 화면 vs 채팅 화면)
if 'app_page' not in st.session_state:
    st.session_state.app_page = 'tutorial'

st.markdown("""
<style>
    .dm-container { display: flex; flex-direction: column; width: 100%; margin-bottom: 15px; }
    .my-msg-box { align-self: flex-end; background-color: #3797F0; color: white; border-radius: 18px 18px 4px 18px; padding: 10px 16px; margin: 2px 0; max-width: 70%; font-size: 15px; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .other-msg-box { align-self: flex-start; background-color: #EFEFEF; color: black; border-radius: 18px 18px 18px 4px; padding: 10px 16px; margin: 2px 0; max-width: 70%; font-size: 15px; box-shadow: 0px 1px 2px rgba(0,0,0,0.05); }
    .sos-msg-box { align-self: flex-start; background-color: #FFEBEB; color: #D32F2F; border: 1px solid #FFCDD2; border-radius: 18px 18px 18px 4px; padding: 12px 16px; margin: 4px 0; max-width: 75%; font-size: 15px; font-weight: bold; animation: pulse 2s infinite; }
    .meta-text { font-size: 11px; color: #8E8E8E; margin-top: 2px; }
    .sender-name { font-size: 12px; color: #555; font-weight: bold; margin-bottom: 2px; margin-left: 5px; }
    .my-sender-name { font-size: 12px; color: #555; font-weight: bold; margin-bottom: 2px; margin-right: 5px; align-self: flex-end; }
    .my-meta { align-self: flex-end; display: flex; gap: 5px; }
    .other-meta { align-self: flex-start; margin-left: 5px; }
    .unread-marker { color: #3797F0; font-weight: bold; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); } 100% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); } }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# [백엔드] 멀티테넌시형 클라우드 데이터베이스 (유저 접속 수 추적 포함)
# -------------------------------------------------------------
@st.cache_resource
def get_global_chat_db():
    # 구조: {"학교코드": {"messages": [], "users": ["학생A", "학생B"]}}
    return {}

global_chat_db = get_global_chat_db()

# 사진을 문자열(Base64)로 변환하는 함수 (클라우드 메모리 저장용)
def get_image_base64(file):
    return base64.b64encode(file.read()).decode()

# -------------------------------------------------------------
# 📄 페이지 1: 사용 설명서 (랜딩 페이지)
# -------------------------------------------------------------
if st.session_state.app_page == 'tutorial':
    st.title("🚨 School-Net 비상 통신망")
    st.markdown("""
    ### 📖 사용 전 꼭 읽어주세요!
    이 앱은 재난 및 비상 상황 발생 시, 학교나 특정 단체 인원들끼리 **안전하게 소통하기 위해 만들어진 비상 메신저**입니다.

    **✅ 1. 학교 고유 ID (비밀번호 역할)**
    * 아무 단어나 입력해도 실시간으로 채팅방이 만들어집니다!
    * 단, 친구들과 대화하려면 **미리 약속한 똑같은 단어**(예: `대원고비상망1`, `우리반생존방`)를 띄어쓰기까지 정확하게 똑같이 입력해야 합니다.

    **✅ 2. 닉네임**
    * 채팅방 안에서 불릴 내 이름이나 별명을 마음대로 입력해 주세요. (예: `2학년3반홍길동`)

    **✅ 3. 카카오톡처럼 작동하는 읽음 표시!**
    * 방에 들어온 접속자 수만큼 읽지 않은 사람의 숫자가 표시되며, 친구들이 화면을 볼 때마다 숫자가 자동으로 줄어듭니다.
    """)
    
    st.divider()
    if st.button("🚀 설명서를 모두 읽었습니다! 채팅 시작하기", use_container_width=True, type="primary"):
        st.session_state.app_page = 'chat'
        st.rerun()

# -------------------------------------------------------------
# 💬 페이지 2: 실제 채팅 화면
# -------------------------------------------------------------
elif st.session_state.app_page == 'chat':
    
    # 실시간 동기화를 위한 주기적 리프레시 커널 (3초)
    st_autorefresh(interval=3000, key="global_chat_synchronizer")

    # 사이드바: 설정 및 예쁜 안내 문구
    with st.sidebar:
        st.header("⚙️ 네트워크 설정")
        
        st.info("💡 **학교 고유 ID란?**\n친구들과 미리 약속한 '비밀방 이름'입니다. 아무 글자나 자유롭게 치면 방이 만들어집니다!")
        school_id = st.text_input("🏫 학교 고유 ID (방 이름)", value="우리끼리_비밀방")
        
        st.info("💡 **닉네임**\n방 안에서 불릴 내 이름을 자유롭게 적어주세요.")
        user_nickname = st.text_input("🙋‍♂️ 내 닉네임", value="학생A")
        
        st.divider()
        if st.button("⬅️ 설명서 다시 보기"):
            st.session_state.app_page = 'tutorial'
            st.rerun()
            
        if st.button("💥 이 방의 모든 대화 파기 (초기화)"):
            if school_id in global_chat_db:
                global_chat_db[school_id]["messages"].clear()
                global_chat_db[school_id]["users"].clear()
                st.rerun()

    # 방이 없으면 실시간으로 개설
    if school_id not in global_chat_db:
        global_chat_db[school_id] = {"messages": [], "users": []}

    current_room = global_chat_db[school_id]

    # [핵심 로직] 현재 유저가 이 방에 처음 들어왔다면 접속자 명단에 추가
    if user_nickname not in current_room["users"]:
        current_room["users"].append(user_nickname)

    total_users_count = len(current_room["users"])

    st.title(f"💬 {school_id}")
    st.caption(f"현재 접속 중인 인원: {total_users_count}명 | 내 닉네임: {user_nickname}")
    st.divider()

    # -------------------------------------------------------------
    # [상태 동기화 엔진] 누가 읽었는지 기록하고, 숫자 계산하기
    # -------------------------------------------------------------
    for msg in current_room["messages"]:
        # 내가 안 읽은 메시지라면 읽음 명단에 내 이름 추가
        if user_nickname not in msg["read_by"] and msg["sender"] != user_nickname:
            msg["read_by"].append(user_nickname)

    # -------------------------------------------------------------
    # [타임라인 렌더링] 메시지 출력
    # -------------------------------------------------------------
    for msg in current_room["messages"]:
        is_me = (msg["sender"] == user_nickname)
        is_sos = msg["is_sos"]
        time_str = msg["timestamp"]
        
        # 카카오톡식 읽음 숫자 계산: 전체인원 - 1(보낸사람) - 읽은사람 수
        unread_count = max(0, total_users_count - 1 - len(msg["read_by"]))
        unread_indicator = f'<span class="unread-marker">{unread_count}</span>' if unread_count > 0 else ''
        
        if is_me:
            st.markdown(f"""
            <div class="dm-container">
                <div class="my-sender-name">{msg['sender']}</div>
                <div class="my-msg-box">{msg['content']}</div>
                <div class="meta-text my-meta">{unread_indicator} <span>{time_str}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            box_class = "sos-msg-box" if is_sos else "other-msg-box"
            prefix = "🚨 [긴급 구조 요청] " if is_sos else ""
            st.markdown(f"""
            <div class="dm-container">
                <div class="sender-name">{msg['sender']}</div>
                <div class="{box_class}">{prefix}{msg['content']}</div>
                <div class="meta-text other-meta">{time_str}</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # [입력부] 사진 전송 (Expander) 및 텍스트 전송
    # -------------------------------------------------------------
    with st.expander("📷 사진 첨부하기"):
        img_file = st.file_uploader("현장 사진을 업로드하세요", type=["png", "jpg", "jpeg"])
        if st.button("사진 전송하기") and img_file:
            b64_str = get_image_base64(img_file)
            img_html = f'<img src="data:image/jpeg;base64,{b64_str}" style="max-width: 100%; border-radius: 10px;">'
            
            new_message = {
                "msg_id": int(time.time() * 1000),
                "sender": user_nickname,
                "content": img_html,
                "is_sos": False,
                "read_by": [], # 처음엔 아무도 안 읽음
                "timestamp": datetime.now().strftime("%H:%M")
            }
            current_room["messages"].append(new_message)
            st.rerun()

    chat_input = st.chat_input("메시지를 입력하세요... (SOS, 구조 등 단어 입력 시 자동 사이렌)")
    if chat_input:
        # 개인정보 마스킹 로직
        clean_text = re.sub(r'01[016789]-\d{3,4}-\d{4}', '010-****-****', chat_input)
        clean_text = re.sub(r'\d{6}-[1234]\d{6}', lambda m: m.group().split('-')[0] + '-*******', clean_text)
        
        # SOS 감지
        sos_keywords = ["구조", "도와주세요", "SOS", "sos", "살려주세요", "고립", "화재"]
        sos_trigger = any(kw in clean_text for kw in sos_keywords)
        
        new_message = {
            "msg_id": int(time.time() * 1000),
            "sender": user_nickname,
            "content": clean_text,
            "is_sos": sos_trigger,
            "read_by": [], # 처음엔 아무도 안 읽음
            "timestamp": datetime.now().strftime("%H:%M")
        }
        
        current_room["messages"].append(new_message)
        st.rerun()
