#! /bin/env python

import sys
import readline

from Ollama import Ollama

# Uses Ollama.chat() to hold a conversation between user and LLM, with a few extra system commands
def main():
	# usage: chat.py <optional: model>
	model = "llama3.1"
	if len(sys.argv) > 1:
		model = sys.argv[1]

	# try to find a matching model name using the search function
	modelname = Ollama.searchModels(model)
	if modelname is None:
		# if we didn't find one, tell the user what choices they have
		models = Ollama.listModels()
		print(f"No model named '{model}' is available!", file=sys.stderr)
		print(f"The available models are:\n\t{(chr(10)+chr(9)).join(models)}", file=sys.stderr)
		return

	# default ip is localhost, default port is Ollama default (11434)
	ol = Ollama(modelname)

	try:
		while True:
			msg = input(f"{ol.depth()+1} >> ")

			# this uses the "/command" system to order system actions in-band
			if msg[0] == '/':
				cmd = msg[1:]

				# exits the program
				if cmd == "quit":
					raise KeyboardInterrupt

				# clears all stored messages
				elif cmd == "clear":
					ol.clear()
					print("= Context cleared...")
					continue

				# swaps who said what and then asks the LLM to reply to it's own last message (since now it's "from the user")
				elif cmd == "flip":
					data = ol.pop()
					if "content" not in data:
						print("= Cannot flip an empty chat...")
						continue
					else:
						msg = data["content"]

					ol.flip()
					print("= Context flipped - LLM will now generate a reply...")

					# this does not continue - it feeds the LLM's last reply back in
					pass

				# remove the LLM's last reply and ask it to try again
				elif cmd == "retry":
					# pop the last LLM message
					data = ol.pop()
					if "content" not in data:
						print("= Cannot retry with an empty chat, ignoring command...")
						continue

					# pop the last user message
					data2 = ol.pop()
					if "content" not in data2:
						print("= Cannot retry with only one message, ignoring command...")
						ol.push(data) # put the first message back since we aren't going to go through with the flip
						continue
					else:
						msg = data["content"]

					# this does not continue - it feeds the user's last message back in
					pass

				# removes the LLM's last message and the user's message before that, effectively "undoing" the user's last message
				elif cmd == "undo":
					# pop the last LLM message
					data = ol.pop()
					if "content" not in data:
						print("= Cannot retry with an empty chat, ignoring command...")
						continue

					# pop the last user message
					data2 = ol.pop()
					if "content" not in data2:
						print("= Cannot retry with only one message, ignoring command...")
						ol.push(data) # put the first message back since we aren't going to go through with the flip

					# restart from one iteration back (1 user, 1 assistant)
					print("= Stepped back")
					continue

				else:
					print(f"= Unknown command '{cmd}'")
					continue

			reply = ol.chat(msg)
			print(f"\n{ol.depth()} << {reply.message}\n")

	except KeyboardInterrupt:
		print("\n= Ending chat...")

	finally:
		if (ol.isLoaded()): ol.unload()


if __name__ == '__main__':
	main()
