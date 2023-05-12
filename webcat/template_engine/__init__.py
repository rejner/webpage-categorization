from .chatGPT import ChatGPTTemplateEngine
from .chatGPT_v2 import ChatGPTTemplateEngine_v2

def list_engines():
    return [
        ChatGPTTemplateEngine_v2(),
        ChatGPTTemplateEngine(),
    ]