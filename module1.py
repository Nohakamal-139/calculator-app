import streamlit as st
import subprocess
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- خطوة الترجمة للينكس (Streamlit Cloud) ---
# بنحدد اسم الملف التنفيذي بناءً على نظام التشغيل
if os.name == 'nt': # لو شغال على ويندوز (جهازك)
    exe_path = "./Numerical_project.exe"
else: # لو شغال على لينكس (السيرفر)
    exe_path = "./my_cpp_app"
    # لو الملف مش موجود، نترجمه فوراً
    if not os.path.exists(exe_path):
        with st.spinner("Compiling C++ backend on server..."):
            # بنستخدم g++ لترجمة الكود
            subprocess.run(["g++", "-O3", "Numerical_project.cpp", "-o", "my_cpp_app"])
            os.chmod(exe_path, 0o755)

# 1. إعدادات الصفحة
st.set_page_config(page_title="Numerical Pro Solver", layout="centered")

# 2. CSS (نفس الستايل الشيك)
st.markdown("""
    <style>
    .main { background-color: #0f1116; }
    div.stButton > button { border-radius: 10px; border: 1px solid #30363d; background-color: #161b22; color: #8b949e; transition: 0.3s; }
    div.stButton > button:hover { border-color: #58a6ff; color: #58a6ff; }
    .result-container { background-color: #1c2128; border-left: 5px solid #2ea043; padding: 25px; border-radius: 15px; margin-top: 20px; color: #e6edf3; }
    .result-title { color: #2ea043; font-size: 24px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .var-row { display: flex; padding: 10px 0; border-bottom: 1px solid #252a30; }
    .var-name { font-size: 20px; color: #58a6ff; font-weight: bold; min-width: 60px; }
    .var-value { font-size: 20px; color: #e6edf3; font-family: 'Consolas', monospace; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'method' not in st.session_state:
    st.session_state.method = "Bisection"

st.markdown("<h2 style='text-align: center; color: #e6edf3;'>📊 Numerical Solver Dashboard</h2>", unsafe_allow_html=True)

# أزرار اختيار الطريقة
cols = st.columns(3)
methods = [("📏 Bisection", "Bisection"), ("⚡ Newton", "Newton"), ("🔢 Gauss-Seidel", "Gauss-Seidel")]
for i, (label, m_name) in enumerate(methods):
    with cols[i]:
        if st.button(label, key=f"btn_{m_name}"):
            st.session_state.method = m_name
            st.rerun()

st.divider()

# منطقة المدخلات
method = st.session_state.method
if method in ["Bisection", "Newton"]:
    func_input = st.text_input("Equation f(x) [Use x**2 for power]:", value="x**2 - 4")
    c1, c2 = st.columns(2)
    if method == "Bisection":
        a_in = c1.number_input("Lower Bound (a):", value=0.0)
        b_in = c2.number_input("Upper Bound (b):", value=5.0)
        args = ["1", func_input.replace("**", "^"), str(a_in), str(b_in)]
    else:
        x0_in = c1.number_input("Initial Guess (x0):", value=1.0)
        args = ["2", func_input.replace("**", "^"), str(x0_in)]
else:
    n = st.number_input("Matrix Size (n):", min_value=2, value=3)
    var_names_str = st.text_input("Variable Names (e.g. x, y, z):", value="x, y, z")
    ca, cb = st.columns([2, 1])
    a_mat = ca.text_area("Matrix A (Row by row):", value="4 1 5\n2 1 2\n3 4 5")
    b_vec = cb.text_input("Vector B:", value="9 8 14")
    args = ["3", str(n)] + a_mat.split() + b_vec.split()

# زر الحساب والرسم
if st.button("🚀 Run Analysis", use_container_width=True):
    if os.path.exists(exe_path):
        if method == "Gauss-Seidel":
            if len(a_mat.split()) + len(b_vec.split()) != n*n + n:
                st.error(f"❌ Input Mismatch.")
                st.stop()

        with st.spinner('Calculating...'):
            res = subprocess.run([exe_path] + args, capture_output=True, text=True, encoding='utf-8')
            raw_output = res.stdout.strip()
            
            if raw_output:
                if "ERROR" in raw_output:
                    st.error(f"❌ {raw_output}")
                else:
                    st.toast("Calculation Successful!", icon="✅")
                    lines = raw_output.split("\n")
                    data = [line.split(",") for line in lines]
                    
                    if method in ["Bisection", "Newton"]:
                        df = pd.DataFrame(data, columns=["Iteration", "x_Value", "f(x)"])
                        final_root = df["x_Value"].iloc[-1]
                        st.markdown(f'<div class="result-container"><div class="result-title">✅ Solution Found:</div><div class="var-row"><span class="var-name">Root</span><span class="var-value">= {final_root}</span></div></div>', unsafe_allow_html=True)
                        st.subheader("📋 Iteration Steps")
                        st.dataframe(df, use_container_width=True)
                        try:
                            st.subheader("📈 Visualization")
                            x_plot = np.linspace(-10, 10, 400)
                            y_plot = [eval(func_input.replace("^", "**"), {"x": xi, "np": np, "sin": np.sin, "cos": np.cos, "exp": np.exp, "sqrt": np.sqrt}) for xi in x_plot]
                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.plot(x_plot, y_plot, color='#58a6ff', linewidth=2)
                            ax.axhline(0, color='white', linewidth=1)
                            root_f = float(final_root)
                            ax.scatter([root_f], [0], color='red', s=150, zorder=5)
                            ax.set_facecolor('#0f1116'); fig.patch.set_facecolor('#0f1116')
                            ax.tick_params(colors='white')
                            st.pyplot(fig)
                        except: st.warning("Visual not available.")
                    
                    else:
                        df = pd.DataFrame(data, columns=["Iteration", "Raw_Values"])
                        names = [n.strip() for n in var_names_str.split(",")]
                        def fmt(s): return " , ".join([f"{names[i] if i<len(names) else f'x{i+1}'}={v}" for i,v in enumerate(s.split())])
                        df["Solution"] = df["Raw_Values"].apply(fmt)
                        st.subheader("📋 Gauss-Seidel Steps")
                        st.dataframe(df[["Iteration", "Solution"]], use_container_width=True)
                        f_res = fmt(df["Raw_Values"].iloc[-1]).replace(" , ", "  |  ")
                        st.markdown(f'<div class="result-container"><div class="result-title">✅ System Solution:</div><div style="font-size:20px; color:#79c0ff; font-family:monospace;">{f_res}</div></div>', unsafe_allow_html=True)
            else:
                st.error("Engine Error.")
    else:
        st.error("C++ Executable could not be created/found.")
