import streamlit as st
import scipy.io as sio
import matplotlib.pyplot as plt
import numpy as np
from ai_report import generate_report
from pdf_report import create_pdf
from tc_analysis import find_tc, detect_outliers
import os

st.set_page_config(page_title="Tc Analysis Platform", layout="wide")
st.title("超导薄膜Tc智能分析平台")

uploaded_file = st.file_uploader("上传MAT文件", type=["mat"])

if uploaded_file:

    mat = sio.loadmat(uploaded_file)
    T_all = mat["T"]
    R_all = mat["R"]

    st.sidebar.header("Tc搜索设置")

    mode = st.sidebar.radio(
        "模式",
        ["自动识别", "手动指定区间"]
    )

    tc_min = None
    tc_max = None

    if mode == "手动指定区间":
        tc_min = st.sidebar.number_input("Tc下限(K)", value=5.0)
        tc_max = st.sidebar.number_input("Tc上限(K)", value=15.0)

    sample_id = st.selectbox(
        "选择样品",
        range(T_all.shape[0])
    )

    T = T_all[sample_id]
    R = R_all[sample_id]

    result = find_tc(T, R, tc_min, tc_max)

    st.subheader("Tc分析结果")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tc", f"{result['Tc']:.3f} K")
    c2.metric("Tc_onset", f"{result['Tc_onset']:.3f} K")
    c3.metric("Tc_end", f"{result['Tc_end']:.3f} K")
    c4.metric("Transition Width", f"{result['Width']:.3f} K")

    st.subheader("样品质量评估")
    c5, c6, c7 = st.columns(3)
    c5.metric("Noise Level", f"{result['NoiseLevel']:.4f}")
    c6.metric("Transition Strength", f"{result['TransitionStrength']:.3f}")
    c7.metric("Quality Score", f"{result['QualityScore']:.1f}")

    st.subheader("系统评价")
    if result["QualityScore"] >= 85:
        st.success("样品质量优秀，超导转变明显。")
    elif result["QualityScore"] >= 70:
        st.warning("样品质量良好，存在进一步优化空间。")
    else:
        st.error("样品质量较差，建议重新制备或测试。")

    st.subheader("R-T曲线")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(T, R, label="Raw Data", alpha=0.6)
    ax.plot(T, result["R_smooth"], linewidth=2, label="Smoothed")
    tc_idx = np.argmin(np.abs(T - result["Tc"]))
    ax.scatter(T[tc_idx], R[tc_idx], s=80, label=f"Tc={result['Tc']:.2f}K")
    if mode == "手动指定区间":
        ax.axvspan(tc_min, tc_max, alpha=0.15)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Resistance (Ohm)")
    ax.legend()
    st.pyplot(fig)

    st.subheader("异常检测")
    outlier_idx = detect_outliers(R)
    st.write(f"发现异常点数量：{len(outlier_idx)}")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(T, R)
    if len(outlier_idx) > 0:
        ax2.scatter(T[outlier_idx], R[outlier_idx], s=20)
    st.pyplot(fig2)

    st.divider()
    st.subheader("AI科研分析报告")
    if st.button("生成AI报告"):
        with st.spinner("Qwen分析中..."):
            report = generate_report(result, len(outlier_idx), sample_id)
        st.markdown(report)

        os.makedirs("reports", exist_ok=True)

        # 保存Markdown报告
        report_file = f"reports/sample_{sample_id}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        # 生成PDF
        pdf_file = create_pdf(result, report, sample_id, fig)

        st.success("AI报告生成成功")

        # 下载PDF
        with open(pdf_file, "rb") as pdf:
            st.download_button(
                label="📄 下载PDF科研报告",
                data=pdf,
                file_name=pdf_file,
                mime="application/pdf"
            )

else:
    st.info("请上传MAT文件")