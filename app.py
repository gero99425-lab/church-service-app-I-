import streamlit as st
import pandas as pd
import os
from datetime import date
from streamlit_cookies_controller import CookieController

# إعداد الصفحة
st.set_page_config(page_title="نظام تحضير الخدمة", page_icon="⛪")

# تشغيل وحدة التحكم في الكوكيز الخاصة بمتصفح المستخدم
controller = CookieController()

# --- ملفات البيانات ---
users_file = "users.csv"
data_file = "data.csv"

# 1. إنشاء الملفات لو مش موجودة
if not os.path.exists(users_file):
    df_users = pd.DataFrame(columns=["Username", "Password"])
    df_users.to_csv(users_file, index=False, encoding='utf-8-sig')

if not os.path.exists(data_file):
    df_empty = pd.DataFrame(columns=["التاريخ", "اسم الخادم", "الموضوع", "الآية"])
    df_empty.to_csv(data_file, index=False, encoding='utf-8-sig')

# --- التحقق من حالة الدخول عبر كوكيز المتصفح الخاصة بالمستخدم فقط ---
cookie_user = controller.get("servant_logged_user")

if "logged_in" not in st.session_state:
    if cookie_user:
        st.session_state.logged_in = True
        st.session_state.username = cookie_user
    else:
        st.session_state.logged_in = False
        st.session_state.username = ""

# --- شاشة تسجيل الدخول ---
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول - نظام الخدمة الكنسية")
    
    input_user = st.text_input("اسم المستخدم")
    input_pass = st.text_input("كلمة المرور", type="password")
    
    col_login, col_signup = st.columns(2)
    
    with col_login:
        if st.button("دخول", use_container_width=True):
            if input_user and input_pass:
                df_users = pd.read_csv(users_file)
                user_row = df_users[(df_users["Username"] == input_user) & (df_users["Password"] == input_pass)]
                if not user_row.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    # حفظ اسم المستخدم في كوكي متصفح هذا المستخدم فقط لمدة أسبوع
                    controller.set("servant_logged_user", input_user, max_age=7*86400)
                    st.rerun()
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
            else:
                st.warning("من فضلك ادخل اسم المستخدم وكلمة المرور.")
                
    with col_signup:
        if st.button("إنشاء حساب جديد", use_container_width=True):
            if input_user and input_pass:
                df_users = pd.read_csv(users_file)
                if input_user in df_users["Username"].values:
                    st.error("اسم المستخدم ده موجود قبل كده!")
                else:
                    new_user = {"Username": input_user, "Password": input_pass}
                    df_users = pd.concat([df_users, pd.DataFrame([new_user])], ignore_index=True)
                    df_users.to_csv(users_file, index=False, encoding='utf-8-sig')
                    st.success("تم إنشاء الحساب بنجاح! اضغط دخول الآن.")
            else:
                st.warning("اكتب اسمك والباسورد عشان تعمل حساب.")

# --- التطبيق الأساسي (بعد تسجيل الدخول) ---
else:
    st.sidebar.success(f"مرحباً بك: {st.session_state.username}")
    
    # زر تسجيل الخروج (يحذف الكوكي الخاصة بالمتصفح فوراً)
    if st.sidebar.button("تسجيل خروج"):
        controller.remove("servant_logged_user")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.title("⛪ نظام إدارة وتحضير الخدمة الكنسية")

    # خانات الإدخال
    col1, col2 = st.columns(2)
    with col1:
        servant_name = st.text_input("اسم الخادم", value=st.session_state.username, disabled=True)
        service_date = st.date_input("تاريخ الخدمة", date.today())
    with col2:
        lesson_topic = st.text_input("موضوع الدرس")
        verse = st.text_input("الآية الذهبية")

    # زر الحفظ
    if st.button("حفظ التحضير الجديد"):
        if lesson_topic.strip() == "":
            st.warning("من فضلك اكتب موضوع الدرس على الأقل!")
        else:
            df = pd.read_csv(data_file)
            new_row = {"التاريخ": service_date, "اسم الخادم": servant_name, "الموضوع": lesson_topic, "الآية": verse}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(data_file, index=False, encoding='utf-8-sig')
            st.success("تم حفظ التحضير بنجاح!")
            st.rerun()

    # --- خانة البحث الذكي ---
    st.markdown("---")
    st.subheader("🔍 البحث في سجل التحضيرات")
    search_query = st.text_input("ابحث باسم الخادم، الموضوع، أو الآية...")

    # --- عرض كل الشغل مع تصفية البحث ---
    st.subheader("سجل التحضيرات الكلي")
    df_show = pd.read_csv(data_file)
    
    if df_show.empty:
        st.info("لا توجد تحضيرات مسجلة حتى الآن.")
    else:
        if search_query:
            mask = df_show.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            df_filtered = df_show[mask]
        else:
            df_filtered = df_show

        st.dataframe(df_filtered, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ حذف تحضيراتك الخاصة")
        
        user_records = df_show[df_show["اسم الخادم"] == st.session_state.username]
        
        if user_records.empty:
            st.caption("ليس لديك تحضيرات مسجلة لحذفها.")
        else:
            for index, row in user_records.iterrows():
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.write(f"📅 **{row['التاريخ']}** | 📖 **{row['الموضوع']}** (الآية: {row['الآية']})")
                with col_btn:
                    if st.button("حذف", key=f"del_{index}"):
                        df_show = df_show.drop(index).reset_index(drop=True)
                        df_show.to_csv(data_file, index=False, encoding='utf-8-sig')
                        st.success("تم الحذف بنجاح!")
                        st.rerun()
