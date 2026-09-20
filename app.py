from datetime import datetime
import os
from PIL import Image
import sqlite3
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="딴딴이의 체험단 매니저",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 모바일 화면 타이틀 줄바꿈 및 간격 최적화 CSS
st.markdown(
    """
    <style>
    h1 {
        font-size: 1.8rem !important;
        word-break: keep-all;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 알림 상태 저장을 위한 세션 스테이트 초기화
if "reg_status" not in st.session_state:
    st.session_state.reg_status = None

# SQLite 데이터베이스 연결 및 테이블 생성
def init_db():
  conn = sqlite3.connect("tanddan_v2.db", check_same_thread=False)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS blog_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            platform TEXT,
            visit_date TEXT,
            deadline TEXT,
            content TEXT,
            status TEXT
        )
    """)
  c.execute("""
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
    """)
  conn.commit()
  return conn


conn = init_db()
c = conn.cursor()

# UI 디자인 영역
try:
  if os.path.exists("tanddan.png"):
    image = Image.open("tanddan.png")
    st.image(image, width=120)
except Exception:
  pass

st.title("🔥 딴딴이의 체험단 매니저")

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["🔥 진행 중인 체험단", "✅ 체험 완료 목록"])

with tab1:
  st.subheader("📍 새로운 체험단 등록")

  with st.form("new_campaign_form", clear_on_submit=True):
    company = st.text_input("업체명", placeholder="예: 강남 고기집 / 역삼 식당")
    platform = st.selectbox(
        "플랫폼 선택", ["강남맛집", "디너의여왕", "뷰스타", "기타 체험단"]
    )

    col1, col2 = st.columns(2)
    with col1:
      visit_date = st.date_input("방문 예정일", value=datetime.today())
    with col2:
      deadline = st.date_input("리뷰 마감일", value=datetime.today())

    content = st.text_area(
        "제공내역", placeholder="예: 3만원 식사권 또는 제품 협찬"
    )
    status = st.selectbox("진행 상태", ["신청중", "선정됨"])

    submitted = st.form_submit_button("🦔 딴딴이 리스트에 추가하기")

    if submitted:
      if not company:
        st.warning("업체명을 입력해주세요!")
      else:
        # 1. 날짜 관계없이 무조건 DB에 먼저 저장합니다.
        c.execute(
            """
                    INSERT INTO blog_data (company, platform, visit_date, deadline, content, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
            (
                company,
                platform,
                visit_date.strftime("%Y-%m-%d"),
                deadline.strftime("%Y-%m-%d"),
                content,
                status,
            ),
        )
        conn.commit()
        
        # 2. 날짜 역전 여부를 확인해서 다음 화면에 띄울 알림 종류를 결정합니다.
        if visit_date > deadline:
            st.session_state.reg_status = "warning"
        else:
            st.session_state.reg_status = "success"
            
        st.rerun()

  # 폼 등록 직후 상태에 따라 알림 띄우기
  if st.session_state.reg_status == "warning":
      col_w1, col_w2 = st.columns([1, 4])
      with col_w1:
          try:
              st.image("warning.jpg", width=80)
          except Exception:
              st.warning("⚠️")
      with col_w2:
          st.warning("🚨 주의: 방문 예정일이 리뷰 마감일보다 늦게 설정되었습니다!\n\n(일정은 정상적으로 등록 완료되었습니다.)")
      st.session_state.reg_status = None
      
  elif st.session_state.reg_status == "success":
      st.success("새로운 체험단이 안전하게 등록되었습니다!")
      st.session_state.reg_status = None

  st.markdown("---")
  st.subheader("📋 현재 진행 중인 목록")

  # --- 추가된 부분: 정렬 필터 기능 ---
  sort_option = st.selectbox(
      "보기 정렬 기준", 
      ["최근 등록순", "방문 예정일 빠른순", "리뷰 마감일 빠른순"]
  )

  # 선택한 기준에 따라 SQL 정렬(ORDER BY) 쿼리 변경
  if sort_option == "방문 예정일 빠른순":
      query = "SELECT id, company, platform, visit_date, deadline, content, status FROM blog_data ORDER BY visit_date ASC"
  elif sort_option == "리뷰 마감일 빠른순":
      query = "SELECT id, company, platform, visit_date, deadline, content, status FROM blog_data ORDER BY deadline ASC"
  else:
      query = "SELECT id, company, platform, visit_date, deadline, content, status FROM blog_data ORDER BY id DESC"

  c.execute(query)
  # -----------------------------------
  
  rows = c.fetchall()

  if not rows:
    st.info("등록된 체험단이 없습니다. 새로운 체험단을 등록해 보세요!")
  else:
    for row in rows:
      row_id, comp, plat, v_date, d_line, cont, stat = row
      with st.expander(f"📌 [{plat}] {comp} (상태: {stat})"):
        st.write(f"**방문 예정일:** {v_date}")
        st.write(f"**리뷰 마감일:** {d_line}")
        st.write(f"**제공내역:** {cont}")
        st.write(f"**진행 상태:** {stat}")

        col_a, col_b = st.columns(2)
        with col_a:
          if st.button("✅ 완료로 이동", key=f"complete_{row_id}"):
            today_str = datetime.today().strftime("%Y-%m-%d")
            c.execute(
                """
                        INSERT INTO completed_data (company, platform, visit_date, deadline, content, status, completed_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                (comp, plat, v_date, d_line, cont, "작성완료", today_str),
            )
            c.execute("DELETE FROM blog_data WHERE id = ?", (row_id,))
            conn.commit()
            st.rerun()
        with col_b:
          if st.button("🗑️ 삭제", key=f"delete_{row_id}"):
            c.execute("DELETE FROM blog_data WHERE id = ?", (row_id,))
            conn.commit()
            st.rerun()

with tab2:
  c.execute(
      "SELECT id, company, platform, visit_date, deadline, content, status,"
      " completed_date FROM completed_data ORDER BY completed_date DESC"
  )
  completed_rows = c.fetchall()

  if not completed_rows:
    st.info("완료된 체험단 내역이 없습니다.")
  else:
    for row in completed_rows:
      row_id, comp, plat, v_date, d_line, cont, stat, comp_date = row
      with st.expander(f"✅ [{plat}] {comp} (완료일: {comp_date})"):
        st.write(f"**방문일:** {v_date}")
        st.write(f"**마감일:** {d_line}")
        st.write(f"**제공내역:** {cont}")
        if st.button("🗑️ 기록 삭제", key=f"del_comp_{row_id}"):
          c.execute("DELETE FROM completed_data WHERE id = ?", (row_id,))
          conn.commit()
          st.rerun()
