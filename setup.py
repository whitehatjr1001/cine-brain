import os

structure = {
    "": [
        ".env", ".gitignore", "Dockerfile", "docker-compose.yml", 
        "Makefile", "README.md", "pyproject.toml", "uv.lock"
    ],
    "docs": [
        "overview.md", "setup.md", "usage.md"
    ],
    "docs/assets": [
        "system_diagram.png", "vibe_flow.png", "insideout_analogy.png"
    ],
    "notebooks": [
        "prototype_vibe_check.ipynb", "dialogue_experiments.ipynb", "plot_structure_playground.ipynb"
    ],
    "scripts": [
        "ingest_movies_db.py", "seed_sample_scripts.py", "export_examples.py"
    ],
    "cinebrain": ["__init__.py"],
    "cinebrain/config": ["__init__.py", "settings.py", "logger.py"],
    "cinebrain/agents": [
        "__init__.py", "idea_validator.py", "vibe_matcher.py",
        "dialogue_writer.py", "plot_consistency_checker.py"
    ],
    "cinebrain/graph": [
        "__init__.py", "flow.py", "nodes.py", "edges.py", "state.py"
    ],
    "cinebrain/integrations": [
        "__init__.py", "imdb_api.py", "trope_detector.py", 
        "emotion_analyzer.py", "llm_wrappers.py"
    ],
    "cinebrain/prompts": [
        "__init__.py", "idea_validation_prompts.py", 
        "dialogue_prompts.py", "trope_match_prompts.py"
    ],
    "cinebrain/memory": ["__init__.py", "vector_store.py"],
    "cinebrain/interfaces": ["__init__.py"],
    "cinebrain/interfaces/cli": ["__init__.py", "run.py"],
    "cinebrain/interfaces/web": ["__init__.py", "api_server.py"],
    "cinebrain/interfaces/chainlit": ["__init__.py", "app.py"],
    "cinebrain/utils": ["__init__.py", "text_cleaner.py", "routing.py", "timing.py"]
}

def create_structure(base_path="."):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    if file.endswith(".py"):
                        f.write(f"# {file}\n")
                    elif file.endswith(".md"):
                        f.write(f"# {file.replace('_', ' ').title()}\n")
                    else:
                        f.write("")

if __name__ == "__main__":
    print("📁 Setting up your CineBrain project structure...")
    create_structure()
    print("✅ Done! Your project skeleton is ready to go.")
