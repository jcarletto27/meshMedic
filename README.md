# MeshMedic

**Automated STL Repair & Diagnostics**

MeshMedic is a secure, containerized web application designed to heal broken 3D models. Powered by the industrial-grade MeshLib C++ engine and wrapped in a user-friendly Streamlit interface, it turns non-manifold geometry into watertight, printable parts.

## Features

* **Instant Diagnostics:** Automatically detects holes, open loops, and degenerate geometry upon upload.
* **3-Stage Repair Protocol:**
    1.  **Degeneracy Fix:** Removes zero-area faces and tiny floating edges.
    2.  **Surgical Suturing:** Iteratively finds and closes open boundary loops.
    3.  **Voxel Reconstruction:** Completely remeshes the model if simple hole-filling fails.
* **Secure Processing:** All file operations occur in RAM (tmpfs). No user data is ever written to the physical server disk.
* **Flexible Export:** Download repaired files as STL or 3MF.

## Quick Start (Docker)

The recommended way to run MeshMedic is via Docker Compose. This ensures all C++ dependencies are present and security limits are enforced.

### Prerequisites
* Docker & Docker Compose

### Deployment
1.  Clone this repository.
2.  Run the stack:
    ```bash
    docker-compose up -d --build
    ```
3.  Access the dashboard at:
    `http://localhost:8501`

## Manual Installation (Local Dev)

If you prefer to run it without Docker (e.g., for development):

**Requirements:** Python 3.10 or 3.11 (x64 only). *Note: MeshLib does not currently support ARM (M1/M2 Macs or Raspberry Pi).*

1.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the app:
    ```bash
    streamlit run app.py
    ```

## Security Architecture

MeshMedic is hardened for production deployment:

* **Non-Root User:** Runs as a restricted `appuser` inside the container.
* **Read-Only Filesystem:** The container's root file system is read-only.
* **Ephemeral Storage:** All uploads and processing happen in a 1GB `tmpfs` RAM disk. Data is instantly wiped upon container restart or manual reset.
* **Resource Limits:** Capped at 2 CPUs and 4GB RAM to prevent large mesh processing from crashing the host server.

## Tech Stack

* **Frontend/UI:** Streamlit
* **Geometry Engine:** MeshLib (mrmeshpy)
* **Visualization:** streamlit-stl
* **Containerization:** Docker (Debian 12 Bookworm)

## License

This project uses MeshLib. Please refer to their licensing terms for commercial usage.
