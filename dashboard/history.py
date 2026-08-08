import streamlit as st
import pandas as pd
from database.session import get_session
from database.models import Inspection

def render():
    st.title("Inspection History")
    
    session = next(get_session())
    inspections = session.query(Inspection).order_by(Inspection.timestamp.desc()).all()
    
    if not inspections:
        st.info("No inspections found in the database.")
        return
        
    data = []
    for insp in inspections:
        data.append({
            "ID": insp.id,
            "Date": insp.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Roll ID": insp.roll_id,
            "Batch ID": insp.batch_id,
            "Quality Score": insp.quality_score,
            "Verdict": insp.final_verdict
        })
        
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
