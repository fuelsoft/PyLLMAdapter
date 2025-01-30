#! /bin/env python

import sys

from Ollama import Ollama

# Uses the Ollama.ask() function to send a message, get a response, and exit
def main():
	# usage: ask.py <message>
	if (len(sys.argv) < 2):
		print("Missing arg: query")
		return

	# default ip is localhost, default port is Ollama default (11434)
	ol = Ollama("llama3.1")
	reply = ol.ask(sys.argv[1])
	ol.unload()

	print(reply.message)

if __name__ == '__main__':
	main()
