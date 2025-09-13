from dataclasses import dataclass, field
from typing import List, Dict, Any, Protocol, Callable
from openai import OpenAI
from config import setup_env


@dataclass(frozen=True)
class ModelConfig:
    model_id: str = "gpt-5"
    temperature: float = 0.2
    max_tokens: int = 1000
    reasoning: dict = field(default_factory=lambda: {"effort": "high"})
    text: dict = field(default_factory=lambda: {
        "verbosity": "low",
    })


GLOBAL_MODEL = ModelConfig()

class ChatModel(Protocol):
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str: ...

class OpenAIChat(ChatModel):
    def __init__(self, cfg: ModelConfig):
        self.cfg = cfg
        self.client = OpenAI()

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        params = dict(
            model=self.cfg.model_id,
            messages=messages,
        )
        if "temperature" in kwargs: params["temperature"] = kwargs["temperature"]
        if "max_tokens"  in kwargs: params["max_tokens"]  = kwargs["max_tokens"]
        if "reasoning" in kwargs: params["reasoning"] = kwargs["reasoning"]
        if "text" in kwargs: params["text"] = kwargs["text"]

        resp = self.client.chat.completions.create(**params)
        return resp.choices[0].message.content

@dataclass
class PromptTemplate:
    template: str

    def render(self, **kwargs) -> str:
        return self.template.format(**kwargs)

@dataclass
class SystemModule:
    name: str
    system_template: PromptTemplate

    def system_message(self, **template_vars) -> Dict[str, str]:
        return {"role": "system", "content": self.system_template.render(**template_vars)}

@dataclass
class StepContext:
    state: Dict[str, Any]
    history: List[Dict[str, str]]
    model: ChatModel

StepFn = Callable[[StepContext], str]

@dataclass
class Pipeline:
    system: SystemModule
    steps: List[StepFn]

    def run(self, *, system_vars: Dict[str, Any], user_input: str, model: ChatModel) -> Dict[str, Any]:
        history = [self.system.system_message(**system_vars)]
        history.append({"role": "user", "content": user_input})

        ctx = StepContext(state={}, history=history, model=model)
        outputs = []

        for step in self.steps:
            out = step(ctx)
            outputs.append(out)
            ctx.history.append({"role": "assistant", "content": out})

        return {"final": outputs[-1] if outputs else "", "all_step_outputs": outputs, "state": ctx.state}

if __name__ == "__main__":
    setup_env()
    model = OpenAIChat(GLOBAL_MODEL)
    print("Patterns module ready for use")