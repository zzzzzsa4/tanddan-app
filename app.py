import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# 앱 페이지 설정 (모바일 최적화 레이아웃)
st.set_page_config(page_title="딴딴이의 체험단 매니저", page_icon="🦔", layout="centered")

# 🎨 딴딴이 테마 커스텀 CSS 디자인 주입
st.markdown("""
    <style>
    .main {
        background-color: #0f1117;
    }
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #f97316, #eab308, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem !important;
        margin-bottom: 0rem;
        word-break: keep-all;
    }
    h3 {
        font-size: 1.1rem !important;
        font-weight: 600;
        color: #e2e8f0;
    }
    div.stForm {
        background: #1e293b;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
        color: white;
        border: none;
        padding: 0.6rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(249, 115, 22, 0.4);
    }
    /* 탭 스타일 최적화 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        color: #94a3b8;
        padding: 10px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 영구 저장소(SQLite) 연결 함수
# ==========================================
def init_db():
    conn = sqlite3.connect("tanddan_v2.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS blog_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, platform TEXT, visit_date TEXT, deadline TEXT, content TEXT, status TEXT, link TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS completed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, platform TEXT, visit_date TEXT, deadline TEXT, content TEXT, status TEXT, link TEXT, completed_date TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()
c = conn.cursor()


# ==========================================
# 상단 타이틀 및 딴딴이 마스코트 영역
# ==========================================
col_img, col_txt = st.columns([1, 2.5])

with col_img:
    try:
        st.image("tanddan.png", width=100)
    except:
        st.write("🦔")

with col_txt:
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("딴딴이의 체험단 매니저")
    st.caption("블로그 체험단 일정과 링크를 한눈에!")

st.markdown("<br>", unsafe_allow_html=True)

# 경고 문구 제어용 세션 스테이트 초기화
if 'warning_type' not in st.session_state:
    st.session_state.warning_type = ""


# ==========================================
# 탭 구성 (진행 중 / 완료 목록)
# ==========================================
tab_ongoing, tab_completed = st.tabs(["🔥 진행 중인 체험단", "✅ 체험 완료 목록"])

# ----------------- [탭 1] 진행 중인 체험단 -----------------
with tab_ongoing:
    st.subheader("📍 새로운 체험단 등록")
    
    with st.form("blog_form", clear_on_submit=True):
        b_name = st.text_input("업체명", placeholder="예: 강남 고기집 / 역삼 식당")
        b_platform_choice = st.selectbox("플랫폼 선택", ["강남맛집", "디너의여왕", "리뷰노트", "기타 웹/앱"])
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            b_visit_date = st.date_input("방문 예정일", value=datetime.today())
        with col_date2:
            b_review_deadline = st.date_input("리뷰 마감일", value=datetime.today())
            
        b_offer = st.text_input("제공내역", placeholder="예: 3만원 식사권 또는 제품 협찬")
        b_status = st.selectbox("진행 상태", ["신청중", "선정됨"])
        
        submitted = st.form_submit_button("🦔 딴딴이 리스트에 추가하기")
        
        if submitted:
            today = datetime.today().date()
            
            if not b_name:
                st.warning("업체명을 입력해주세요.")
            elif b_visit_date < today or b_review_deadline < today:
                st.session_state.warning_type = "past_date"
            else:
                if b_platform_choice == "강남맛집":
                    auto_link = "https://xn--939au0g4vj8sq.net/"
                elif b_platform_choice == "디너의여왕":
                    auto_link = "https://dinnerqueen.net/"
                else:
                    auto_link = ""
                
                # SQLite에 데이터 영구 저장
                c.execute("""
                    INSERT INTO blog_data (company, platform, visit_date, deadline, content, status, link)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (b_name, b_platform_choice, str(b_visit_date), str(b_review_deadline), b_offer, b_status, auto_link))
                conn.commit()
                
                if b_visit_date > b_review_deadline:
                    st.session_state.warning_type = "deadline_error"
                else:
                    st.session_state.warning_type = "success"
                
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 예쁜 경고 문구 및 이미지 출력 영역
    if st.session_state.warning_type == "past_date":
        with st.container():
            col_w1, col_w2 = st.columns([1, 4])
            with col_w1:
                if os.path.exists("warning.png"): st.image("warning.png", width=80)
                elif os.path.exists("warning.jpg"): st.image("warning.jpg", width=80)
                else: st.write("🙅‍♂️")
            with col_w2:
                st.error("🚨 오늘보다 빠른 날짜는 선택할 수 없어요!!\n\n(날짜만 다시 수정하고 버튼을 눌러주세요.)")
        st.session_state.warning_type = ""
        
    elif st.session_state.warning_type == "deadline_error":
        with st.container():
            col_w1, col_w2 = st.columns([1, 4])
            with col_w1:
                if os.path.exists("warning.png"): st.image("warning.png", width=80)
                elif os.path.exists("warning.jpg"): st.image("warning.jpg", width=80)
                else: st.write("🙅‍♂️")
            with col_w2:
                st.warning("🚨 리뷰마감일을 지켜주세요!!\n\n(일정은 목록에 정상적으로 등록되었습니다.)")
        st.session_state.warning_type = ""
        
    elif st.session_state.warning_type == "success":
        st.success("딴딴이가 안전하게 저장했어요!")
        st.session_state.warning_type = ""

    st.subheader("📋 내 체험단 관리 현황")

    # DB에서 현재 진행중인 데이터 불러오기
    current_df = pd.read_sql("SELECT id, company as 업체명, platform as 플랫폼, visit_date as 방문예정일, deadline as 리뷰마감일, content as 제공내역, status as 상태, link as 링크 FROM blog_data", conn)

    if not current_df.empty:
        # D-Day 뱃지 생성 함수
        def get_dday_badge(date_str):
            try:
                today = datetime.today().date()
                deadline = pd.to_datetime(str(date_str)).date()
                diff = (deadline - today).days
                
                if diff < 0: return f"💥 D+{abs(diff)} (초과)"
                elif diff == 0: return "🚨 D-Day"
                elif diff <= 2: return f"🚨 D-{diff}"
                elif diff <= 5: return f"⚠️ D-{diff}"
                else: return f"✅ D-{diff}"
            except:
                return "-"

        # 선택 열과 디데이 열 추가
        current_df.insert(0, '선택', False)
        current_df.insert(5, '디데이', current_df['리뷰마감일'].apply(get_dday_badge))

        # 체크박스가 있는 표(data_editor) 생성
        edited_df = st.data_editor(
            current_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None, # 고유번호는 화면에 숨김
                "선택": st.column_config.CheckboxColumn(" ", default=False),
                "링크": st.column_config.LinkColumn("바로가기", display_text="🔗 이동")
            },
            key="blog_editor"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ 체크한 항목 체험 완료"):
                checked_rows = edited_df[edited_df['선택'] == True]
                if not checked_rows.empty:
                    today_str = datetime.today().strftime("%Y-%m-%d")
                    for _, row in checked_rows.iterrows():
                        # 완료 테이블로 데이터 복사
                        c.execute("""
                            INSERT INTO completed_data (company, platform, visit_date, deadline, content, status, link, completed_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (row['업체명'], row['플랫폼'], row['방문예정일'], row['리뷰마감일'], row['제공내역'], "작성완료", row['링크'], today_str))
                        # 원본 테이블에서 삭제
                        c.execute("DELETE FROM blog_data WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
                else:
                    st.warning("체크된 항목이 없습니다.")
                    
        with col_btn2:
            if st.button("🗑️ 체크한 항목 삭제하기"):
                checked_rows = edited_df[edited_df['선택'] == True]
                if not checked_rows.empty:
                    for _, row in checked_rows.iterrows():
                        c.execute("DELETE FROM blog_data WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
                else:
                    st.warning("체크된 항목이 없습니다.")
    else:
        st.info("💡 등록된 체험단이 없습니다. 위에서 새로운 일정을 추가해 보세요!")

# ----------------- [탭 2] 체험 완료 목록 -----------------
with tab_completed:
    st.subheader("🎉 자랑스러운 체험 완료 퀘스트")
    
    comp_df = pd.read_sql("SELECT id, company as 업체명, platform as 플랫폼, visit_date as 방문예정일, deadline as 리뷰마감일, content as 제공내역, status as 상태, link as 링크, completed_date as 완료일 FROM completed_data", conn)
    
    if not comp_df.empty:
        comp_df.insert(0, '선택', False)
        
        comp_edited_df = st.data_editor(
            comp_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None, # 고유번호 숨김
                "선택": st.column_config.CheckboxColumn(" ", default=False),
                "링크": st.column_config.LinkColumn("바로가기", display_text="🔗 이동")
            },
            key="completed_editor"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ 완료 목록에서 영구 삭제"):
            checked_rows = comp_edited_df[comp_edited_df['선택'] == True]
            if not checked_rows.empty:
                for _, row in checked_rows.iterrows():
                    c.execute("DELETE FROM completed_data WHERE id=?", (row['id'],))
                conn.commit()
                st.rerun()
            else:
                st.warning("체크된 항목이 없습니다.")
    else:
        st.info("아직 완료된 체험단이 없습니다. 열심히 다녀오세요!")
