#! /bin/env python

import sys

from Ollama import Ollama

# Uses Ollama.unloadAll() to unload all models on the target machine
def main():
	# default ip is localhost, default port is Ollama default (11434)
	Ollama.unloadAll()

if __name__ == '__main__':
	main()
