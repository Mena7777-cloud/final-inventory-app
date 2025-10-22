import streamlit as st
from database import SessionLocal, Product, User, verify_password, hash_password

st.set_page_config(page_title="نظام المخزون", layout="wide", initial_sidebar_state="auto")

# --- دالة لإنشاء المستخدم الأدمن عند أول تشغيل فقط ---
def create_initial_admin():
    db_check = SessionLocal()
    try:
        admin_user = db_check.query(User).filter(User.username == 'admin').first()
        if not admin_user:
            hashed_pw = hash_password('1234')
            new_admin = User(username='admin', password_hash=hashed_pw)
            db_check.add(new_admin)
            db_check.commit()
            st.toast("تم إنشاء حساب الأدمن الافتراضي بنجاح!")
    finally:
        db_check.close()

# استدعاء الدالة عند بدء تشغيل التطبيق
create_initial_admin()
# ---------------------------------------------

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 تسجيل الدخول - نظام إدارة المخزون")
                
    with st.form("login_form"):
        username = st.text_input("اسم المستخدم", value="admin")
        password = st.text_input("كلمة المرور", type="password", value="1234")
        submitted = st.form_submit_button("تسجيل الدخول")
                    
        if submitted:
            db = SessionLocal()
            user = db.query(User).filter(User.username == username).first()
            db.close()
            if user and verify_password(password, user.password_hash):
                st.session_state.logged_in = True
                st.session_state.username = user.username
                st.experimental_rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
else:
    # --- واجهة التطبيق الرئيسية ---
    st.sidebar.title(f"👋 أهلاً, {st.session_state.username}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    st.title("📦 نظام إدارة المخزون الاحترافي")
                
    db = SessionLocal()

    tab1, tab2 = st.tabs(["📊 عرض وإدارة المخزون", "➕ إضافة منتج جديد"])

    with tab1:
        st.header("قائمة المنتجات")
        products = db.query(Product).order_by(Product.id).all()
                    
        if not products:
            st.info("المخزون فارغ حالياً. يمكنك إضافة منتجات من التاب المجاور.")
        else:
            for p in products:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                col1.text_input("اسم المنتج", p.name, key=f"name_{p.id}", disabled=True)
                col2.text_input("الكمية", p.quantity, key=f"qty_{p.id}", disabled=True)
                col3.text_input("السعر", f"{p.price:.2f}", key=f"price_{p.id}", disabled=True)
                if col4.button("🗑️", key=f"del_{p.id}", help="حذف المنتج"):
                    db.delete(p)
                    db.commit()
                    st.experimental_rerun()
            st.divider()

    with tab2:
        st.header("إضافة منتج")
        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("اسم المنتج")
            quantity = st.number_input("الكمية", min_value=0, step=1)
            price = st.number_input("السعر", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("✅ إضافة المنتج للمخزون")

            if submitted:
                if not name:
                    st.warning("الرجاء إدخال اسم المنتج.")
                else:
                    new_product = Product(name=name, quantity=quantity, price=price)
                    db.add(new_product)
                    db.commit()
                    st.success(f"تمت إضافة المنتج '{name}' بنجاح!")
                
    db.close()
