# PyLLMAdapter

## A simple Python adapter for your Ollama instance

This is the core `Ollama.py` library file and a set of example scripts, including:

* `ask.py` for one time message-and-answer
* `chat.py` to have a multi-message conversation with an LLM
* `complete.py` to demonstrate the fill-in-the-blank ability of some models
* `inspect.py` to send an image and have the LLM analyze the contents
* `unload.py` to quickly unload all models from the command line

These examples all assume that you're running your Ollama instance on your local machine (`localhost:11434`). You can pass IP and port to the constructor to override this.

All examples use sensible default models. You can change them to whatever you'd like, but keep model ability and intended use-case in mind.

*I am aware that there is an official Ollama Python library and I don't care, I'm not installing it when I could get everything I need done in less than 300 lines.*
