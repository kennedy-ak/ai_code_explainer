import streamlit as st
import tempfile
import os
import sys

# Add error handling for deployment environment
try:
    from ultralytics import YOLO
    yolo_available = True
except ImportError as e:
    st.error(f"Error importing YOLO: {e}")
    st.info("Installing missing dependencies...")
    yolo_available = False

st.set_page_config(page_title="YOLO Posture Detection", layout="wide")
st.title("🧍‍♂️ YOLO Posture Detection")
st.markdown("Upload an image to detect human postures using your trained YOLO models.")

# For Streamlit deployment - install system dependencies if needed
if not yolo_available:
    st.warning("Setting up environment. This may take a moment...")
    
    # Check if we're in Linux environment (likely Streamlit Cloud)
    if sys.platform.startswith('linux'):
        try:
            # Install required system libraries
            os.system("apt-get update && apt-get install -y libgl1-mesa-glx")
            # Reinstall ultralytics
            os.system("pip install --force-reinstall ultralytics")
            from ultralytics import YOLO
            yolo_available = True
            st.success("Dependencies installed successfully!")
        except Exception as e:
            st.error(f"Failed to install dependencies: {e}")
            st.stop()

# Load models with caching
@st.cache_resource
def load_model(model_version):
    model_paths = {
        "YOLOv10": "yolov10/best.pt",
        "YOLOv11": "yolov11/best.pt",
        "YOLOv12": "yolov12/best.pt"
    }
    
    if model_version in model_paths:
        try:
            model = YOLO(model_paths[model_version])
            return model
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return None
    else:
        st.error(f"Model {model_version} not found!")
        return None

# File uploader
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_path = tmp_file.name
        tmp_file.write(uploaded_file.read())

    # Display the uploaded image
    st.image(tmp_path, caption="Uploaded Image", use_container_width=True)
    
    # Model selection
    model_version = st.selectbox(
        "Select YOLO model version",
        ["YOLOv10", "YOLOv11", "YOLOv12"],
        index=0
    )
    
    # Run detection button
    if st.button(f"🔍 Run Detection with {model_version}"):
        with st.spinner(f"Running inference with {model_version}..."):
            try:
                # Load the selected model
                model = load_model(model_version)
                
                if model:
                    # Run inference with error handling
                    try:
                        results = model.predict(source=tmp_path, conf=0.3)
                        
                        # Display results
                        result_img = results[0].plot()
                        st.image(result_img, caption=f"{model_version} Detection Result", use_container_width=True)
                        
                        # Show class info
                        if hasattr(model, 'names'):
                            st.markdown("### Class Labels")
                            st.write(model.names)
                            
                            # Show detection confidence scores
                            if len(results[0].boxes) > 0:
                                st.markdown("### Detection Results")
                                
                                # Create a dataframe to display results
                                detections_data = []
                                for i, box in enumerate(results[0].boxes):
                                    class_id = int(box.cls[0].item())
                                    class_name = model.names[class_id]
                                    confidence = round(box.conf[0].item() * 100, 2)
                                    detections_data.append({
                                        "Detection #": i+1,
                                        "Class": class_name,
                                        "Confidence": f"{confidence}%"
                                    })
                                
                                st.table(detections_data)
                            else:
                                st.info("No detections found in this image.")
                    except Exception as e:
                        st.error(f"Error during inference: {e}")
                        st.error("Try uploading a different image or selecting a different model.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    
    # Clean up temp file when the app is done
    if 'tmp_path' in locals():
        try:
            os.remove(tmp_path)
        except:
            pass
else:
    st.info("Please upload an image to get started.")
    
    # Show a preview of available models
    st.markdown("### Available Models")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**YOLOv10**")
        st.markdown("Original YOLO model version")
    
    with col2:
        st.markdown("**YOLOv11**")
        st.markdown("Enhanced version with improved accuracy")
    
    with col3:
        st.markdown("**YOLOv12**")
        st.markdown("Latest version with advanced features")