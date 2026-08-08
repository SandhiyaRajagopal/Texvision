import streamlit as st
import os
import uuid
import datetime
import pandas as pd
from PIL import Image

from database.session import get_session
from database.models import Inspection, Defect
from detection.inference import DefectDetector
from measurement.calculator import calculate_dimensions
from analysis.severity import determine_severity
from suggestion_engine.rules import generate_suggestion
from decision_engine.scorer import calculate_quality_score, determine_final_verdict
from report.generator import generate_pdf_report
from config.settings import UPLOAD_DIR, OUTPUT_DIR, REPORTS_DIR

@st.cache_resource
def load_detector():
    return DefectDetector()

# Force reload if model file changed
if "model_path_loaded" not in st.session_state:
    load_detector.clear()
    st.session_state["model_path_loaded"] = True

def render():
    st.title("New Inspection")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name")
        operator_name = st.text_input("Operator Name")
        roll_id = st.text_input("Roll ID")
    with col2:
        batch_id = st.text_input("Batch ID")
        fabric_type = st.text_input("Fabric Type")
        
    conf_threshold = st.slider("Detection Sensitivity (Lower = More Sensitive)", min_value=0.01, max_value=1.0, value=0.15, step=0.01, help="Decrease this value if defects are not being detected.")
    uploaded_file = st.file_uploader("Upload Image or Video", type=['jpg', 'jpeg', 'png', 'mp4'])
    
    if st.button("Start Inspection", type="primary"):
        if not (company_name and operator_name and roll_id and batch_id and fabric_type and uploaded_file):
            st.error("Please fill all details and upload a file.")
            return
            
        # Ensure it's an image for now (video can be implemented similarly)
        if not uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            st.warning("Video processing is designed for architecture but currently image pipeline is fully implemented.")
            return

        with st.spinner("Processing Inspection..."):
            # 1. Save uploaded file
            file_ext = os.path.splitext(uploaded_file.name)[1]
            temp_path = UPLOAD_DIR / f"temp_{uuid.uuid4().hex}{file_ext}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            # 2. Run Inference
            detector = load_detector()
            if not detector.model:
                st.error("Detection model is not loaded. Please check model path in settings.")
                return
                
            results = detector.predict(str(temp_path), conf_threshold=conf_threshold)
            raw_defects = detector.process_results(results)
            
            # Fallback for base YOLO models which don't know "Stain"
            if not raw_defects:
                raw_defects = detector.fallback_detect(str(temp_path), conf_threshold)
            
            # 3. Process each defect
            processed_defects = []
            for d in raw_defects:
                dims = calculate_dimensions(d['box'])
                d.update(dims)
                d['severity'] = determine_severity(d['class_name'], d['area_cm2'])
                d['suggestion'] = generate_suggestion(d['class_name'], d['severity'])
                processed_defects.append(d)
                
            # 4. Decision Engine
            quality_score = calculate_quality_score(processed_defects)
            verdict = determine_final_verdict(quality_score, processed_defects)
            
            # 5. Annotate Image
            inspection_id = f"INSP-{uuid.uuid4().hex[:8].upper()}"
            annotated_img_path = OUTPUT_DIR / f"{inspection_id}_annotated.jpg"
            detector.annotate_image(str(temp_path), processed_defects, str(annotated_img_path))
            
            # 6. Database storage
            session = next(get_session())
            inspection_record = Inspection(
                id=inspection_id,
                company_name=company_name,
                operator_name=operator_name,
                roll_id=roll_id,
                batch_id=batch_id,
                fabric_type=fabric_type,
                quality_score=quality_score,
                final_verdict=verdict,
                annotated_image_path=str(annotated_img_path)
            )
            session.add(inspection_record)
            
            db_defects = []
            for pd_def in processed_defects:
                defect_record = Defect(
                    inspection_id=inspection_id,
                    defect_type=pd_def['class_name'],
                    confidence=pd_def['confidence'],
                    x_center=pd_def['x_center'],
                    y_center=pd_def['y_center'],
                    width_cm=pd_def['width_cm'],
                    height_cm=pd_def['height_cm'],
                    area_cm2=pd_def['area_cm2'],
                    severity=pd_def['severity'],
                    suggestion=pd_def['suggestion']
                )
                db_defects.append(defect_record)
                session.add(defect_record)
            
            # 7. Generate PDF
            pdf_path = REPORTS_DIR / f"{inspection_id}_report.pdf"
            inspection_record.report_path = str(pdf_path)
            session.commit()
            
            generate_pdf_report(inspection_record, processed_defects, str(pdf_path))
            
        st.success("Inspection Completed!")
        
        # Display Results
        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.image(str(annotated_img_path), caption="Annotated Result", use_container_width=True)
            
        with res_col2:
            st.metric("Quality Score", f"{quality_score}/100")
            if verdict == "PASS":
                st.success("Verdict: PASS")
            elif verdict == "REWORK":
                st.warning("Verdict: REWORK")
            else:
                st.error("Verdict: REJECT")
                
            st.markdown(f"**Total Defects Detected:** {len(processed_defects)}")
            
        if processed_defects:
            df = pd.DataFrame(processed_defects)
            st.dataframe(df[['class_name', 'confidence', 'width_cm', 'height_cm', 'area_cm2', 'severity', 'suggestion']])
            
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name=f"{inspection_id}_report.pdf",
                mime="application/pdf"
            )
