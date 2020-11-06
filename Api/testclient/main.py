import json
import typing

import requests

if typing.TYPE_CHECKING:
	from testclient.api.response import Response as api_Response

from testclient.api.client import Client as api_Client
from testclient.api.models.login import Login
from testclient.api.models.posts import Posts
from testclient.api.models.rooms import Rooms
from testclient.api.models.rooms_users import RoomsUsers
from testclient.api.models.users import Users
from testclient.api.models.users_bans import UsersBans
from testclient.api.models.rooms_bans import RoomsBans


def main():
	client = api_Client("http://127.0.0.1:4200")
	login = Login(client)
	users = Users(client)
	rooms = Rooms(client)
	rooms_users = RoomsUsers(client)
	posts = Posts(client)
	users_bans = UsersBans(client)
	rooms_bans = RoomsBans(client)

	choices = {
		"Users": {
			"Register": users.create,
			"Get": users.get,
			"Get all": users.get_all,
			"Update": users.update,
			"Delete": users.delete,
			"Delete self": users.delete_self
		},
		"Rooms": {
			"Create": rooms.create,
			"Get": rooms.get,
			"Get all": rooms.get_all,
			"Update": rooms.update,
			"Delete": rooms.delete
		},
		"Rooms users": {
			"Create": rooms_users.create,
			"Get": rooms_users.get,
			"Get all": rooms_users.get_all,
			"Delete": rooms_users.delete,
		},
		"Posts": {
			"Create": posts.create,
			"Get": posts.get,
			"Get all": posts.get_all,
			"Update": posts.update,
			"Delete": posts.delete
		},
		"Users bans": {
			"Create": users_bans.create,
			"Get": users_bans.get,
			"Get all": users_bans.get_all,
			"Update": users_bans.update,
			"Delete": users_bans.delete
		},
		"Rooms bans": {
			"Create": rooms_bans.create,
			"Get": rooms_bans.get,
			"Get all": rooms_bans.get_all,
			"Update": rooms_bans.update,
			"Delete": rooms_bans.delete
		},
		"Login": login.login,
		"Logout": login.logout,
		"Quit": None,
	}

	while True:
		choice = get_dict_input(choices)
		if choice is None: break

		try:
			response = run_function(choice)
			if response is not None:
				print(f"Response {response.code}:")
				print("No content" if response.body is None else json.dumps(response.body, indent=2))
			else:
				print("")
		except requests.exceptions.ConnectionError as e:
			print(f"Connection error: {e}")


def run_function(function) -> 'api_Response':
	varnames = function.__code__.co_varnames[1:function.__code__.co_argcount]
	varvalues = []
	for name in varnames:
		input_string = input(f"{name}: ")

		if input_string == "false":
			value = False
		elif input_string == "true":
			value = True
		elif input_string == "":
			value = None
		else:
			value = input_string

		varvalues.append(value)
	return function(*varvalues)


def get_dict_input(choices: dict):
	keys = list(choices.keys())
	for i, key in enumerate(keys): print(f"[{i}]{key}\t", end="")
	print()
	choice = choices[keys[try_get_int_input()]]
	if isinstance(choice, dict):
		return get_dict_input(choice)
	return choice


def try_get_int_input(text: str = ""):
	try:
		return int(input(text))
	except ValueError as e:
		print(f"Error: {e}")
		print("Try again:")
		return try_get_int_input(text)


if __name__ == "__main__":
	main()
