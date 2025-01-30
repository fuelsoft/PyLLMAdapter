#! /bin/env python

import sys

from Ollama import Ollama

# Uses Ollama.ask() to ask the model about the contents of an image file
def main():
	# usage: inspect.py <image file> <optional: message>
	if (len(sys.argv) < 2):
		print("Missing arg: <image path>")
		return

	if (len(sys.argv) < 3):
		query = "What's in this image?"
	else:
		query = sys.argv[2]

	file = []
	with open(sys.argv[1], 'rb') as f:
		file = f.read()

	# default ip is localhost, default port is Ollama default (11434)
	ol = Ollama("llava:13b") # llava is the 'old reliable' of LLM vision models
	reply = ol.ask(query, [file], temperature = 0.1)
	ol.unload()

	print(reply.message)

if __name__ == '__main__':
	main()
