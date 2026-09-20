import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import sqlite3
import os

# 페이지 기본 설정 (모바일 최적화 및 와이드 레이아웃)
st.set_page_config(
    page_title="딴딴이의 체험단 매니저",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# SQLite 데이터베이스 연결 및 테이블 생성 (각 사용자 폰 내부의 독립 저장소)
def init_db():
    conn = sqlite3.connect('local_tanddan.db', check_same_thread=False)
    c = conn.cursor()
    # 진행 중인 체험단 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS blog_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            platform TEXT,
            visit_date TEXT,
            deadline TEXT,
            content TEXT,
            status TEXT
        )
    ''')
    # 체험 완료 목록 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS completed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            platform TEXT,
            visit_date TEXT,
            deadline TEXT,
            content TEXT,
            status TEXT,
            completed_date TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# 데이터 로드 함수
def load_data(table_name):
    query = f"SELECT company, platform, visit_date, deadline, content, status FROM {table_name}"
    if table_name == 'completed_data':
        query = f"SELECT company, platform, visit_date, deadline, content, status, completed_date FROM {table_name}"
    df = pd.read_sql(query, conn)
    return df

# 데이터 저장 함수
def save_data(df, table_name):
    df.to_sql(table_name, conn, if_exists='replace', index=False)

# 기본 데이터프레임 구조 정의
df_columns = ['업체명', '플랫폼', '방문 예정일', '리뷰 마감일', '제공내역', '진행 상태']
completed_columns = ['업체명', '플랫폼', '방문 예정일', '리뷰 마감일', '제공내역', '진행 상태', '완료일']

current_df = load_data('blog_data')
if current_df.empty:
    current_df = pd.DataFrame(columns=df_columns)
else:
    current_df.columns = df_columns

completed_df = load_data('completed_data')
if completed_df.empty:
    completed_df = pd.DataFrame(columns=completed_columns)
else:
    completed_df.columns = completed_columns

# UI 디자인 영역
try:
    if os.path.exists("tanddan.png"):
        image = Image.open("tanddan.png")
        st.image(image, width=120)
except Exception:
    pass

st.title("🔥 딴딴이의 체험단 매니저")
st.markdown("블로그 체험단 일정과 링크를 내 폰에서 완벽하게 한눈에!")

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["🔥 진행 중인 체험단", "✅ 체험 완료 목록"])

with tab1:
    st.subheader("📍 새로운 체험단 등록")
    
    with st.form("new_campaign_form", clear_on_submit=True):
        company = st.text_input("업체명", placeholder="예: 강남 고기집 / 역삼 식당")
        platform = st.selectbox("플랫폼 선택", ["강남맛집", "디너의여왕", "뷰스타", "기타 체험단"])
        
        col1, col2 = st.columns(2)
        with col1:
            visit_date = st.date_input("방문 예정일", value=datetime.today())
        with col2:
            deadline = st.date_input("리뷰 마감일", value=datetime.today())
            
        content = st.text_area("제공내역", placeholder="예: 3만원 식사권 또는 제품 협찬")
        status = st.selectbox("진행 상태", ["신청중", "선정됨", "방문완료", "작성완료"])
        
        submitted = st.form_submit_button("🦔 딴딴이 리스트에 추가하기")
        
        if submitted:
            if company:
                new_row = pd.DataFrame([[
                    company, platform, 
                    visit_date.strftime("%Y-%m-%d"), 
                    deadline.strftime("%Y-%m-%d"), 
                    content, status
                ]], columns=df_columns)
                
                current_df = pd.concat([current_df, new_row], ignore_index=True)
                save_data(current_df, 'blog_data')
                st.success("새로운 체험단이 안전하게 등록되었습니다!")
                st.rerun()
            else:
                st.warning("업체명을 입력해주세요!")

    st.markdown("---")
    st.subheader("📋 현재 진행 중인 목록")
    
    if current_df.empty:
        st.info("등록된 체험단이 없습니다. 새로운 체험단을 등록해 보세요!")
    else:
        for idx, row in current_df.iterrows():
            with st.expander(f"📌 [{row['플랫폼'
            ]}] {row['업체명']} (상태: {row['진행 상태']})"):
                st.write(f"**방문 예정일:** {row['방문 예정일']}")
                st.write(f"**리뷰 마감일:** {row['리뷰 마감일']}")
                st.write(f"**제공내역:** {row['제공내역']}")
                st.write(f"**진행 상태:** {row['진행 상태']}")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ 완료로 이동", key=f"complete_{idx}"):
                        completed_row = pd.DataFrame([[
                            row['업체명'], row['플랫폼'], row['방문 예정일'], 
                            row['리뷰 마감일'], row['제공내역'], "작성완료", 
                            datetime.today().strftime("%Y-%m-%d")
                        ]], columns=completed_columns)
                        
                        completed_df = pd.concat([completed_df, completed_row], ignore_index=True)
                        save_data(completed_df, 'completed_data')
                        
                        current_df = current_df.drop(idx).reset_index(drop=True)
                        save_data(current_df, 'blog_data')
                        st.rerun()
                with col_b:
                    if st.button("🗑️ 삭제", key=f"delete_{idx}"):
                        current_df = current_df.drop(idx).reset_index(drop=True)
                        save_data(current_df, 'blog_data')
                        st.rerun()

with tab2:
    st.subheader("🏆 완료된 체험단 아카이브")
    if completed_df.empty:
        st.info("완료된 체험단 내역이 없습니다.")
    else:
        for idx, row in completed_df.iterrows():
            with st.expander(f"✅ [{row['플랫폼']}] {row['업체명']} (완료일: {row.get('완료일', '정보 없음')})"):
                st.write(f"**방문일:** {row['방문 예정일']}")
                st.write(f"**마감일:** {row['리뷰 마감일']}")
                st.write(f"**제공내역:** {row['제공내역']}")
                if st.button("🗑️ 기록 삭제", key=f"del_comp_{idx}"):
                    completed_df = completed_df.drop(idx).reset_index(drop=True)
                    save_data(completed_df, 'completed_data')
                    st.rerun()
