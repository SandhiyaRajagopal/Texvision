import streamlit as st
import pandas as pd
import plotly.express as px
from database.session import get_session
from database.models import Inspection, Defect

def render():
    st.title("Analytics Dashboard")
    
    session = next(get_session())
    
    # KPIs
    total_inspections = session.query(Inspection).count()
    if total_inspections == 0:
        st.info("No data available for analytics.")
        return
        
    passed = session.query(Inspection).filter_by(final_verdict="PASS").count()
    rework = session.query(Inspection).filter_by(final_verdict="REWORK").count()
    rejected = session.query(Inspection).filter_by(final_verdict="REJECT").count()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Inspections", total_inspections)
    col2.metric("Pass Rate", f"{(passed/total_inspections)*100:.1f}%")
    col3.metric("Rework Rate", f"{(rework/total_inspections)*100:.1f}%")
    col4.metric("Reject Rate", f"{(rejected/total_inspections)*100:.1f}%")
    
    # Charts
    st.markdown("### Verdict Distribution")
    verdict_df = pd.DataFrame({
        "Verdict": ["PASS", "REWORK", "REJECT"],
        "Count": [passed, rework, rejected]
    })
    fig_verdict = px.pie(verdict_df, names="Verdict", values="Count", color="Verdict",
                         color_discrete_map={"PASS": "green", "REWORK": "orange", "REJECT": "red"})
    st.plotly_chart(fig_verdict, use_container_width=True)
    
    # Defect Distribution
    st.markdown("### Most Common Defects")
    defects = session.query(Defect).all()
    if defects:
        defect_types = [d.defect_type for d in defects]
        defect_df = pd.DataFrame(defect_types, columns=["Defect Type"])
        defect_counts = defect_df["Defect Type"].value_counts().reset_index()
        defect_counts.columns = ["Defect Type", "Count"]
        
        fig_defects = px.bar(defect_counts, x="Defect Type", y="Count", color="Defect Type")
        st.plotly_chart(fig_defects, use_container_width=True)
