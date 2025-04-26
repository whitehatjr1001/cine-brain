# CineBrain AI

CineBrain is an AI-powered multi-agent system designed to support scriptwriters and filmmakers throughout the creative process. From brainstorming ideas and writing dialogue to generating visuals, audio, and validating story structure, CineBrain combines specialized AI agents under a unified orchestration framework to bring your cinematic vision to life.

## 🚀 Key Features

- **Idea Generation**: Brainstorm original story and scene ideas.
- **Dialogue Assistance**: Craft natural, emotionally rich character conversations.
- **Vibe Matching**: Compare your synopsis to tone and style of successful movies.
- **Plot Consistency**: Detect logical issues, pacing problems, and plot holes.
- **Box Office Prediction**: Estimate commercial potential based on genre and audience.
- **Visual Storyboarding**: Generate scene imagery via text-to-image agents.
- **Audio Rendering**: Convert script dialogue into spoken samples (text-to-speech).
- **Memory & Personalization**: Extract and remember user preferences and story facts.
- **Smart Routing**: Orchestrate agents with Chain-of-Thought reasoning for immediate answers or delegation.
- **Extensible Architecture**: Plug in new agents, integrations, and deployment targets.

## 📁 Project Structure

\`\`\`plaintext
cine-brain/
├── .env                   # Environment variables (API keys, configs)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── setup.py
├── src/
│   ├── config/
│   │   ├── settings.py    # Centralized config and .env loader
│   │   └── logger.py      # Logging setup
│   ├── prompts.py         # All prompt templates for agents
│   ├── integrations/      # External service wrappers (LLM, TTS, Image APIs)
│   ├── agents/            # AI agent implementations (idea, dialogue, etc.)
│   ├── agent_graph/       # LangGraph orchestration: nodes, edges, router
│   ├── utils/             # Helper functions and chains
│   └── interfaces/        # CLI, web API, Chainlit app entrypoints
├── docs/                  # Project documentation and diagrams
├── notebooks/             # Research and experiments
└── todo.txt               # Sprint plan and tasks
\`\`\`

## 🛠️ Installation & Setup

1. **Clone the repository:**
   \`\`\`bash
   git clone https://github.com/your-org/cine-brain.git
   cd cine-brain
   \`\`\`

2. **Create a virtual environment and install dependencies:**
   \`\`\`bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   \`\`\`

3. **Configure environment variables:**
   - Copy \`.env.example\` to \`.env\` and fill in API keys for LLM, TTS, and Image services.

4. **Run initial tests:**
   \`\`\`bash
   pytest
   \`\`\`

## 📖 Usage

### 1. Run the CLI
\`\`\`bash
uv run src/interfaces/cli/run.py
\`\`\`
Follow the prompts to interact with the CineBrain assistant.

### 2. Start the Web API
\`\`\`bash
uv run src/interfaces/web/api_server.py
\`\`\`
Open \`http://localhost:8000/docs\` for Swagger UI.

### 3. Launch the Chainlit App
\`\`\`bash
uv run src/interfaces/chainlit/app.py
\`\`\`

## 🗂️ Workflow Example

1. **User**: "Give me a thriller short film idea."
2. **Router** analyzes and invokes **idea_generator**.
3. **Idea Generator** returns 3 concise ideas.
4. **User**: "Show me a storyboard image for idea #2."
5. **Router** invokes **image_scenario** and **storyboard_agent**.
6. **System** returns an image or visual prompt.
7. **User**: "Read it aloud." → **tts_agent** produces audio.

## 🤝 Contributing

- Fork the repo and create a feature branch.
- Ensure all new code is covered by tests.
- Open a Pull Request with a clear description of your changes.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

_Created with ❤️ by the CineBrain Team_
