import streamlit as st
import meshlib.mrmeshpy as mm
from streamlit_stl import stl_from_file
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="MeshMedic", layout="wide", page_icon="🚑")

TMP_DIR = os.environ.get('TMPDIR', '/tmp/stl_processing')
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file):
    temp_path = os.path.join(TMP_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def cleanup_files():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- HEADER ---
st.title("🚑 MeshMedic")
st.markdown("**Automated STL Repair & Diagnostics** | Powered by MeshLib")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Control Panel")
    if st.button("🗑️ Discharge Patient (Reset)", type="primary"):
        cleanup_files()
    st.info("Files are processed securely in RAM.")

# --- MAIN LOGIC ---
uploaded_file = st.file_uploader("Upload 3D Model", type=['stl'])

if uploaded_file:
    # Save file on first load
    if 'current_file' not in st.session_state or st.session_state.get('uploaded_name') != uploaded_file.name:
        saved_path = save_uploaded_file(uploaded_file)
        if saved_path:
            st.session_state['current_file'] = saved_path
            st.session_state['uploaded_name'] = uploaded_file.name
            st.session_state['repair_done'] = False 

    col1, col2 = st.columns([1, 1])

    # --- LEFT COLUMN: DIAGNOSTICS ---
    with col1:
        st.subheader("📋 Diagnostics")
        if 'current_file' in st.session_state:
            try:
                # Load mesh
                mesh = mm.loadMesh(st.session_state['current_file'])
                
                # Metric Counting
                vert_count = mesh.topology.getValidVerts().count()
                face_count = mesh.topology.getValidFaces().count()
                
                # Hole detection (Vector of Vectors)
                hole_loops = mm.findRightBoundary(mesh.topology)
                num_holes = hole_loops.size()
                
                is_watertight = (num_holes == 0)
                
                metrics = {
                    "Vertices": vert_count,
                    "Faces": face_count,
                    "Status": "✅ Healthy (Watertight)" if is_watertight else "❌ Critical (Holes Detected)",
                    "Open Loops": num_holes
                }
                st.dataframe(metrics, use_container_width=True)

                st.write("### X-Ray Preview")
                stl_from_file(file_path=st.session_state['current_file'], color='#e74c3c' if not is_watertight else '#2ecc71', height=400)
            except Exception as e:
                st.error(f"Failed to load mesh: {e}")

    # --- RIGHT COLUMN: TREATMENT ---
    with col2:
        st.subheader("💊 Treatment Plan")
        
        if st.button("🚀 Begin Surgery (Repair)"):
            status = st.status("Performing procedure...", expanded=True)
            try:
                # 1. Degeneracies
                status.write("🔍 Removed degenerate geometry...")
                params = mm.FixMeshDegeneraciesParams()
                mm.fixMeshDegeneracies(mesh, params)
                
                # 2. Holes
                status.write("🧵 Suturing holes...")
                fill_params = mm.FillHoleParams()
                fill_params.metric = mm.getUniversalMetric(mesh)
                
                max_holes = 500
                i = 0
                while i < max_holes:
                    boundaries = mm.findRightBoundary(mesh.topology)
                    if boundaries.size() == 0:
                        break
                    
                    first_loop = boundaries[0]
                    if first_loop.size() == 0:
                        break
                        
                    edge_id = first_loop[0]
                    mm.fillHole(mesh, edge_id, fill_params)
                    i += 1

                # 3. Voxel Remesh (The "Cure All")
                status.write("🧬 Reconstructing topology (Voxel Remesh)...")
                
                # Calculate safe voxel size based on object scale
                bbox = mesh.computeBoundingBox()
                diag = bbox.diagonal()
                
                if diag < 1e-5:
                    raise ValueError("Mesh is empty or microscopic.")
                
                # 600 resolution gives a slightly sharper result than 500
                safe_voxel_size = diag / 600.0
                
                offset_params = mm.OffsetParameters()
                offset_params.voxelSize = safe_voxel_size
                
                mesh = mm.offsetMesh(mesh, 0.0, offset_params)
                
                status.update(label="Surgery Successful!", state="complete", expanded=False)
                
                # Export
                output_base = st.session_state['current_file'].replace(".stl", "_fixed")
                mm.saveMesh(mesh, output_base + ".stl")
                mm.saveMesh(mesh, output_base + ".3mf")
                
                st.session_state['output_base'] = output_base
                st.session_state['repair_done'] = True
                
            except Exception as e:
                status.update(label="Procedure Failed", state="error")
                st.error(f"Error: {str(e)}")

        if st.session_state.get('repair_done'):
            st.divider()
            fmt = st.radio("Output Format:", ["STL", "3MF"], horizontal=True)
            ext = ".stl" if fmt == "STL" else ".3mf"
            
            with open(st.session_state['output_base'] + ext, "rb") as f:
                st.download_button(
                    label=f"💾 Discharge Patient ({fmt})",
                    data=f,
                    file_name=f"meshmedic_repaired{ext}",
                    mime="application/octet-stream",
                    type="primary"
                )
