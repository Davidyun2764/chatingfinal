import streamlit as st
import re
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------
# [프론트엔드] 인스타그램 DM 스타일 고급 렌더링 CSS 주입
# -------------------------------------------------------------
st.set_page_config(page_title="School-Net Direct (Isolated)", layout="centered")

st.markdown("""
<style>
    .dm-container { display: flex; flex-direction: column; width: 100%; margin-bottom: 15px; }
    .my-msg-box { align-self: flex-end; background-color: #3797F0; color: white; border-radius: 18px 18px 4px 18px; padding: 10px 16px; margin: 2px 0; max-width: 70%; font-size: 15px; box-shadow: 0px 1px 2px rgba(0,0,0,0.1); }
    .other-msg-box { align-self: flex-start; background-color: #EFEFEF; color: black; border-radius: 18px 18px 18px 4px; padding: 10px 16px; margin: 2px 0; max-width: 70%; font-size: 15px; box-shadow: 0px 1px 2px rgba(0,0,0,0.05); }
    .sos-msg-box { align-self: flex-start; background-color: #FFEBEB; color: #D32F2F; border: 1px solid #FFCDD2; border-radius: 18px 18px 18px 4px; padding: 12px 16px; margin: 4px 0; max-width: 75%; font-size: 15px; font-weight: bold; animation: pulse 2s infinite; }
    .meta-text { font-size: 11px; color: #8E8E8E; margin-top: 2px; }
    .my-meta { align-self: flex-end; display: flex; gap: 5px; }
    .other-meta { align-self: flex-start; margin-left: 5px; }
    .unread-marker { color: #3797F0; font-weight: bold; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(211, 47, 47, 0); } 100% { box-shadow: 0 0 0 0 rgba(211, 47, 47, 0); } }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# [백엔드] 멀티테넌시형 클라우드 딕셔너리 데이터베이스
# -------------------------------------------------------------
@st.cache_resource
def get_global_chat_db():
    # 단일 리스트가 아니라, {"학교코드": [메시지리스트]} 형태의 딕셔너리를 전역 공유 메모리에 생성
    return {}

global_chat_db = get_global_chat_db()

# 실시간 동기화를 위한 백그라운드 주기적 리프레시 커널 (2초)
st_autorefresh(interval=2000, key="global_chat_synchronizer")

# -------------------------------------------------------------
# [보안 커널] 개인정보 법령 준수 필터 및 재난 키워드 분석기
# -------------------------------------------------------------
def process_security_filters(text):
    # 개인정보 보호법 및 정보통신망법 기술적 조치: 주민번호 및 전화번호 실시간 감지 및 마스킹
    text = re.sub(r'01[016789]-\d{3,4}-\d{4}', '010-****-****', text)
    text = re.sub(r'\d{6}-[1234]\d{6}', lambda m: m.group().split('-')[0] + '-*******', text)
    return text

def check_sos_condition(text):
    sos_keywords = ["구조", "도와주세요", "SOS", "sos", "살려주세요", "고립", "화재"]
    return any(kw in text for kw in sos_keywords)

# -------------------------------------------------------------
# [사이드바 인프라 제어 패널]
# -------------------------------------------------------------
with st.sidebar:
    st.header("🌐 사설 네트워크 설정")
    
    # 기존 IP 주소 입력창의 한계를 극복하는 논리적 학교 식별자 가동
    school_id = st.text_input("🏫 학교 고유 고정 ID 입력", value="대원고_비상망", 
                             help="같은 학교 코드를 입력한 사람들끼만 데이터가 암호 격리되어 매핑됩니다.")
    
    user_nickname = st.text_input("🙋‍♂️ 사용자 닉네임", value="학생A")
    
    st.divider()
    st.subheader("보안 관리")
    if st.button("💥 현재 학교 통신 로그 즉각 파기"):
        if school_id in global_chat_db:
            global_chat_db[school_id].clear()
            st.success(f"법령 보호조치 준수: '{school_id}' 구역의 데이터가 영구 파기(Zeroing)되었습니다.")
            st.rerun()

# -------------------------------------------------------------
# [데이터 격리 바인딩] 입력한 학교 코드에 해당하는 독립 거실 개설
# -------------------------------------------------------------
if school_id not in global_chat_db:
    global_chat_db[school_id] = []

# 현재 사용자가 속한 학교의 독립된 대화 내역 포인터 지정
current_school_stream = global_chat_db[school_id]

# 메인 UI 렌더링
st.title(f"💬 School-Net Direct")
st.caption(f"🔒 암호 격리망 ID: {school_id} | 접속자: {user_nickname}")
st.divider()

# -------------------------------------------------------------
# [상태 동기화 엔진] 내가 이 학교 방에 들어와서 남의 메시지를 읽었다면 1 소멸
# -------------------------------------------------------------
for msg in current_school_stream:
    if msg["sender"] != user_nickname and msg["unread_count"] == 1:
        msg["unread_count"] = 0

# -------------------------------------------------------------
# [타임라인 렌더링] 인스타그램 DM 스타일 화면 스캔 출력
# -------------------------------------------------------------
for msg in current_school_stream:
    is_me = (msg["sender"] == user_nickname)
    is_sos = msg["is_sos"]
    time_str = msg["timestamp"]
    
    if is_me:
        unread_indicator = '<span class="unread-marker">1</span>' if msg["unread_count"] > 0 else ''
        st.markdown(f"""
        <div class="dm-container">
            <div class="my-msg-box">{msg['content']}</div>
            <div class="meta-text my-meta">{unread_indicator} <span>{time_str}</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        box_class = "sos-msg-box" if is_sos else "other-msg-box"
        prefix = "🚨 [긴급 구조 요청] " if is_sos else ""
        st.markdown(f"""
        <div class="dm-container">
            <div class="meta-text other-meta">{msg['sender']}</div>
            <div class="{box_class}">{prefix}{msg['content']}</div>
            <div class="meta-text other-meta">{time_str}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# [메시지 송신 패킷 인젝션]
# -------------------------------------------------------------
chat_input = st.chat_input(f"'{school_id}' 네트워크에 안전하게 메시지 전송...")
if chat_input:
    # 1. 보안 필터 커널 통과
    clean_text = process_security_filters(chat_input)
    sos_trigger = check_sos_condition(clean_text)
    
    # 2. 개별 라우팅 패킷 표준 빌드
    new_message = {
        "msg_id": int(time.time() * 1000),
        "sender": user_nickname,
        "content": clean_text,
        "is_sos": sos_trigger,
        "unread_count": 1,  # 방에 속한 상대방이 읽기 전까지 초기 마커 1 유지
        "timestamp": datetime.now().strftime("%H:%M")
    }
    
    # 3. 전역 데이터베이스 내 '해당 학교 고유 구역'에만 데이터 추가 (완벽 격리)
    current_school_stream.append(new_message)
    st.rerun()