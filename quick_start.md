# CoffeeGen-Plant

**CoffeeGen-Plant** is a procedural framework for generating 3D models of coffee plants that are both structurally coherent and visually realistic. Unlike purely geometric approaches, our system employs a graph-based architecture that explicitly encodes the plant's morphology. This enables the automatic extraction of annotations and structural attributes, making it ideal for applications in digital agriculture, phenotyping, digital twins, and synthetic data generation for computer vision. The project also includes an open dataset featuring photorealistic materials for coffee plant leaves and trunks. For further details, please consult our paper at: [link to be updated soon].

---

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MaVILab-UFV/CoffeeGen-Plant.git
   cd CoffeeGen-Plant
   ```

2. **Create and Activate a Virtual Environment**
   * **Windows:**
     ```cmd
     python -m venv environment
     .\environment\Scripts\activate
     ```
   * **Linux / macOS:**
     ```bash
     python3 -m venv environment
     source environment/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Basic Usage

1. **Configure Parameters**  
   Open `config.py` and adjust the configuration parameters according to your experiment or desired plant architecture.

2. **Generate the 3D Model**  
   Execute the main script:
   ```bash
   python main.py
   ```
   This process produces two primary output files:
   * `pe_de_cafe.json` (structural metadata)
   * `pe_de_cafe.obj` (3D mesh)

---

## FBX Export via Blender

To process the generated plant data inside Blender and export it as an FBX model with materials:

1. **Prerequisites**  
   Ensure **Blender 5.0** is installed on your system.

2. **Configure Script Paths**  
   Open `create_coffee_blender.py` and set the required absolute paths:
   * `base_path`: Absolute path to the project directory.
   * `json_path`: Absolute path to `pe_de_cafe.json`.

3. **Run the Script in Blender**  
   Open Blender, launch the **Python Console** (or Scripting workspace), and execute:
   ```python
   import os
   os.chdir("path/to/absolute/directory/project")
   exec(open("create_coffee_blender.py").read())
   ```

4. **Export FBX**  
   Once generated in the scene, export the model and its associated materials via **File > Export > FBX (.fbx)**.
