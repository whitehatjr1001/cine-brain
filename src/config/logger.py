from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
import logging
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel

class LogCategory(Enum):
    AGENT = "agent"
    SCRIPT = "script"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    CRITICAL = "critical"

class LogColors(BaseModel):
    AGENT: str = "cyan"
    SCRIPT: str = "green"
    WORKFLOW: str = "blue"
    SYSTEM: str = "magenta"
    ERROR: str = "red"
    WARNING: str = "orange3"
    INFO: str = "white"
    DEBUG: str = "grey70"
    CRITICAL: str = "red bold"

class CineBrainLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'logger'):
            custom_theme = Theme({
                f"{cat.value}": getattr(LogColors(), cat.name.upper(), "white")
                for cat in LogCategory
            })
            self.console = Console(theme=custom_theme)
            self.logger = logging.getLogger("cinebrain")
            self.logger.setLevel(logging.DEBUG)
            rich_handler = RichHandler(
                console=self.console,
                rich_tracebacks=True,
                show_time=True,
                show_path=True,
                markup=True
            )
            rich_handler.setLevel(logging.DEBUG)
            self.logger.handlers.clear()
            self.logger.addHandler(rich_handler)

    def _log(self, level: int, message: str, category: LogCategory, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        ctx_str = ""
        if context:
            ctx_str = " | " + " | ".join(f"{k}: {v}" for k, v in context.items())
        styled_message = f"[{category.value}]{message}{ctx_str}[/{category.value}]"
        self.logger.log(level, styled_message, **kwargs)

    def agent_event(self, agent_name: str, event: str, details: Optional[str] = None, workflow_stage: Optional[str] = None, **kwargs) -> None:
        context = {"agent": agent_name}
        if workflow_stage:
            context["stage"] = workflow_stage
        if details:
            context["details"] = details
        self._log(logging.INFO, f"Agent Event: {event}", LogCategory.AGENT, context, **kwargs)

    def script_step(self, step: str, agent_name: Optional[str] = None, details: Optional[str] = None, **kwargs) -> None:
        context = {"step": step}
        if agent_name:
            context["agent"] = agent_name
        if details:
            context["details"] = details
        self._log(logging.INFO, f"Script Step: {step}", LogCategory.SCRIPT, context, **kwargs)

    def workflow_transition(self, from_stage: str, to_stage: str, agent_name: Optional[str] = None, **kwargs) -> None:
        context = {"from": from_stage, "to": to_stage}
        if agent_name:
            context["agent"] = agent_name
        self._log(logging.INFO, f"Workflow Transition: {from_stage} -> {to_stage}", LogCategory.WORKFLOW, context, **kwargs)

    def workflow_error(self, error: str, agent_name: Optional[str] = None, stage: Optional[str] = None, exc_info: Optional[bool] = True, **kwargs) -> None:
        context = {"error": error}
        if agent_name:
            context["agent"] = agent_name
        if stage:
            context["stage"] = stage
        self._log(logging.ERROR, f"Workflow Error: {error}", LogCategory.ERROR, context, exc_info=exc_info, **kwargs)

    def system_info(self, message: str, **kwargs) -> None:
        self._log(logging.INFO, message, LogCategory.SYSTEM, **kwargs)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        self._log(logging.WARNING, f"⚠️ {message}", LogCategory.WARNING, context, **kwargs)

    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        context["debug"] = True
        self._log(logging.DEBUG, message, LogCategory.DEBUG, context, **kwargs)

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        context["critical"] = True
        self._log(logging.CRITICAL, f"🚨 {message}", LogCategory.CRITICAL, context, **kwargs)

    def exception(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        ctx_str = ""
        if context:
            ctx_str = " | " + " | ".join(f"{k}: {v}" for k, v in context.items())
        self.logger.exception(f"❌ {message}{ctx_str}")

logger = CineBrainLogger()
