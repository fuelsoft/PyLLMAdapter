#! /bin/env python

# A super lightweight and easy to use LLM adapter for Ollama

import sys
import json
import base64
from requests import post, get

class Ollama():
	# setup data
	model = ""
	ip = ""
	port = 0

	# user chat data
	messages = []

	# if things aren't working, you may want to check that the requests being sent are right
	__debug_requests = False;

	def __init__(self, model, ip = "localhost", port = 11434):
		self.model = model
		self.ip = ip
		self.port = port

	# ask the current server to load the current model in preparation for a message
	# this is optional, calling ask() or chat() will also load the model
	def load(self, keep_loaded_for = "5m"):
		url = f"http://{self.ip}:{self.port}/api/generate"
		headers = {'Content-Type': 'application/json'}
		data = {"model": self.model, "keep_alive": keep_loaded_for}
		post(url, headers = headers, data = json.dumps(data))

	# ask the current server to unload the current model
	def unload(self):
		url = f"http://{self.ip}:{self.port}/api/generate"
		headers = {'Content-Type': 'application/json'}
		data = {"model": self.model, "keep_alive": 0}
		post(url, headers = headers, data = json.dumps(data))

	# a message chain where previous messages are fed in as additional context to allow a conversation
	def chat(self, query, images = [], temperature = 0.7):
		url = f"http://{self.ip}:{self.port}/api/chat"
		headers = {'Content-Type': 'application/json'}
		data = {
			"model": self.model,
			"messages": [
				{
					"role": "system",
					"content": "Reply to the following message from the user."
				}
			],
			"stream": False,
			"options": {
				"temperature": temperature
			}
		}

		for message in self.messages:
			data["messages"].append(message)

		message = {
			"role": "user",
			"content": query
		}

		if len(images) > 0:
			preparedImages = []
			for image in images:
				if not isinstance(image, str):
					image = base64.b64encode(image).decode("utf-8")

				preparedImages.append(image)
			message["images"] = preparedImages

		data["messages"].append(message)
		data["options"]["temperature"] = temperature

		if self.__debug_requests:
			print(f"\n\n\t{json.dumps(data)}\n\n")

		req = post(url, headers = headers, data = json.dumps(data))
		if not req.ok:
			print(req.reason, file = sys.stderr)
			return None

		reply = Reply(json.loads(req.text))

		# push 
		self.push({"role": "user", "content": query})
		self.push({"role": "assistant", "content": reply.message})

		return reply

	# a one-shot message and response that does not retain any memory from one call to the next
	def ask(self, query, images = [], temperature = 0.7):
		url = f"http://{self.ip}:{self.port}/api/generate"
		headers = {'Content-Type': 'application/json'}
		data = {
			"model": self.model,
			"prompt": query,
			"stream": False,
			"options": {
				"temperature": temperature
			}
		}

		if len(images) > 0:
			preparedImages = []
			for image in images:
				if not isinstance(image, str):
					image = base64.b64encode(image).decode("utf-8")

				preparedImages.append(image)
			data["images"] = preparedImages

		if self.__debug_requests:
			print(f"\n\n\t{json.dumps(data)}\n\n")

		req = post(url, headers = headers, data = json.dumps(data))
		if not req.ok:
			print(req.reason, file = sys.stderr)
			return None

		return Reply(json.loads(req.text))

	# given how a string starts and ends, try to fill in the blank in the middle
	def complete(self, before, after, temperature = 0.7):
		url = f"http://{self.ip}:{self.port}/api/generate"
		headers = {'Content-Type': 'application/json'}
		data = {
			"model": self.model,
			"prompt": before,
			"suffix": after,
			"stream": False,
			"options": {
				"temperature": temperature
			}
		}

		if self.__debug_requests:
			print(f"\n\n\t{json.dumps(data)}\n\n")

		req = post(url, headers = headers, data = json.dumps(data))
		if not req.ok:
			print(f"HTTP {req.status_code}: {json.loads(req.text)['error']}")
			return None

		return Reply(json.loads(req.text))

	# flip ownership of messages (You -> LLM, LLM -> You)
	def flip(self):
		for i, message in enumerate(self.messages):
			if message["role"] == "user":
				self.messages[i]["role"] = "assistant"
			elif message["role"] == "assistant":
				self.messages[i]["role"] = "user"

	# add a message to the end of your chat
	def push(self, message):
		self.messages.append(message)

	# remove the last message from the end of your chat (if it exists)
	def pop(self):
		if len(self.messages) == 0:
			return {}

		msg = self.messages[-1]
		self.messages = self.messages[:-1]
		return msg

	# how many messages long the current chat is
	def depth(self):
		return len(self.messages)

	# remove the current chat's message history
	def clear(self):
		self.messages = []

	# check if the current model is currently loaded on the current server
	def isLoaded(self):
		url = f"http://{self.ip}:{self.port}/api/ps"
		headers = {'Content-Type': 'application/json'}

		req = get(url, headers = headers)
		if not req.ok:
			print(req.reason, file = sys.stderr)
			return False

		data = json.loads(req.text)
		for model in data["models"]:
			if model["name"] == self.model:
				return True

		return False

	# get a list of available models on the specified server
	@staticmethod
	def listModels(ip = "localhost", port = 11434):
		url = f"http://{ip}:{port}/api/tags"
		headers = {'Content-Type': 'application/json'}

		req = get(url, headers = headers)
		if not req.ok:
			print(req.reason, file = sys.stderr)
			return []

		data = json.loads(req.text)
		return [model["name"] for model in data["models"]]

	# search for a model by name on the specified server, returning the exact model name (or None for no match)
	@staticmethod
	def searchModels(search, ip = "localhost", port = 11434):
		matches = []

		models = Ollama.listModels(ip, port)
		for model in models:
			if model.find(search) >= 0:
				matches.append(model)

		if len(matches) == 0:
			return None

		return sorted(matches, key=lambda s: (len(s[:s.find(':')]), s))[0]

	# request that the specified server unload all models that it has loaded currently
	@staticmethod
	def unloadAll(ip = "localhost", port = 11434):
		psUrl = f"http://{ip}:{port}/api/ps"
		unloadUrl = f"http://{ip}:{port}/api/generate"
		headers = {'Content-Type': 'application/json'}

		req = get(psUrl, headers = headers)
		if not req.ok:
			print(req.reason, file = sys.stderr)
			return

		data = json.loads(req.text)
		for model in data["models"]:
			post(unloadUrl, headers = headers, data = json.dumps({"model": model["model"], "keep_alive": 0}))

# when the LLM replies, you'll get one of these back
# they contain the message and some metadat about the call
class Reply():
	def __init__(self, data):
		self.raw = data
		if "response" in data: # completion ('ask')
			self.message = data["response"]
		else: # chat
			self.message = data["message"]["content"]

		if "total_duration" in data:
			self.duration = data["total_duration"]
		else:
			self.duration = 0
			print(f"Reply did not contain a duration value: {json.dumps(data)}", file = sys.stderr)

	# remove leading/trailing whitespace, and optionally strip the closing period (if it exists)
	def stripped(self, remove_dot = False):
		string = self.message.strip()
		if remove_dot and string.endswith('.'):
			return string[:-1]
		return string
