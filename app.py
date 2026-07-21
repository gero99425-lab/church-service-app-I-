import streamlit as st
import datetime
import pandas as pd
import os

st.set_page_config(page_title="نظام إدارة وتحضير الخدمة الكنسية", page_icon="⛪", layout="centered")

# التأكد من حالة تسجيل الدخول مرة واحدة للجلسة
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# إذا لم يسجل الدخول بعد، تظهر شاشة تسجيل الدخول مرة واحدة فقط
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>⛪ تسجيل دخول خادم الخدمة الكنسية</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.form("login_form"):
        name_input = st.text_input("أدخل اسمك الكريم للبدء:")
        submit_login = st.form_submit_button("دخول للنظام")
        
        if submit_login:
            if name_input.strip() != "":
                st.session_state.logged_in = True
                st.session_state.username = name_input.strip()
                st.rerun()
            else:
                st.error("الرجاء كتابة الاسم بشكل صحيح.")
else:
    # واجهة التطبيق الرئيسية (تظهر مباشرة طالما تم تسجيل الدخول)
    st.sidebar.markdown(f"**أهلاً بك، {st.session_state.username}**")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("<h1 style='text-align: center;'>⛪ نظام إدارة وتحضير الخدمة الكنسية</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # نموذج تحضير الدرس الكامل
    with st.form("service_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            servant_name = st.text_input("اسم الخادم", value=st.session_state.username, disabled=True)
            service_date = st.date_input("تاريخ الخدمة", datetime.date.today())
            
        with col2:
            lesson_topic = st.text_input("موضوع الدرس")
            golden_verse = st.text_input("الآية الذهبية")
            
        submit_button = st.form_submit_button(label="حفظ التحضير الجديد")
        
        if submit_button:
            if lesson_topic:
                st.success(f"تم حفظ تحضير درس ({lesson_topic}) بنجاح بواسطة الخادم: {st.session_state.username}!")
            else:
                st.warning("من فضلك أدخل موضوع الدرس على الأقل.")

    st.markdown("---")
    st.markdown("### 🔍 البحث في سجل التحضيرات")
    search_query = st.text_input("ابحث باسم الخادم، الموضوع، أو الآية...")
    
    if search_query:
        st.info(f'جاري البحث عن: "{search_query}"...')
