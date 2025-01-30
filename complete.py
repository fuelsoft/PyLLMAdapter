#! /bin/env python

import sys

from Ollama import Ollama

# Uses Ollama.complete() to generate Python function using a fill-in-the-blank completion system
def main():
	# the formatting of these strings is a bit weird but it prints a lot nicer at the end like this
	before = "# python 3 logging function\n# print and save the string to the specified file\ndef logToFile(filename, str):"
	after = "\tf.close()"

	# default ip is localhost, default port is Ollama default (11434)
	# <!> A small warning here, many code models do not support Ollama's "insert" capability out of the box. !<!>
	# <!> Codestral and Codellama specifically are like this, so you will not be able to use them here. <!>
	ol = Ollama("deepseek-coder-v2:latest")
	reply = ol.complete(before, after)
	ol.unload()

	print(f"{before} {reply.message} {after}")

if __name__ == '__main__':
	main()
