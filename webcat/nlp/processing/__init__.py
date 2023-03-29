import os
from template_engine import ChatGPTTemplateEngine


if __name__ == "__main__":
    # set env OPENAI_API_KEY
    os.environ['OPENAI_API_KEY'] = "sk-xxxxxxxxxxxxxxxxxxx"

    engine = ChatGPTTemplateEngine()
    engine.template_from_file("/workspaces/webpage_categorization/data/bungee54-forums/bungee54-forums/2014-11-05/viewtopic.php_pid=4282")
    # engine.template_from_file("/workspaces/webpage_categorization/data/tortuga-forums/2014-01-01/viewtopic.php_p=22")