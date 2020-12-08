import json
import os
import threading
from http import HTTPStatus
from pathlib import Path

import argon2
import flask
import isodate
import requests
import werkzeug
from flask_cors import CORS

import controllers.login
import controllers.posts
import controllers.rooms
import controllers.rooms_bans
import controllers.rooms_users
import controllers.users
import controllers.users_bans
import core.auth.jwt
import core.database
import main
import models.posts
import models.rooms
import models.rooms_bans
import models.rooms_users
import models.users
import models.users_bans
import routes
import services.auth
import services.request
import services.users
from core.config import Config

SERVER_ADDRESS = "http://127.0.0.1:4200"


def chdir():
	os.chdir(Path(os.path.abspath(__file__)).parent)


# noinspection PyMethodMayBeStatic
class RConfig:
	@staticmethod
	def get():
		chdir()
		return Config("./", "config")


# noinspection PyMethodMayBeStatic
class RDatabase:
	@staticmethod
	def _get_db_password():
		chdir()
		with open("dbpass") as file:
			return file.readline()

	@staticmethod
	def get():
		cfg = RConfig.get()
		return core.database.Database(
			cfg[cfg.DB_HOST], cfg[cfg.DB_PORT],
			cfg[cfg.DB_NAME], cfg[cfg.DB_SCHEMA],
			cfg[cfg.DB_USER], RDatabase._get_db_password()
		)


# noinspection PyMethodMayBeStatic
class RServer:
	_app_thread: threading.Thread

	def start(self):
		cfg = RConfig.get()
		private_key = core.auth.jwt.read_private_key(cfg[cfg.TOKENS_PRIVATE_KEY_PATH])
		public_key = core.auth.jwt.read_public_key(cfg[cfg.TOKENS_PUBLIC_KEY_PATH])
		tokens_lifetime = isodate.parse_duration(cfg[cfg.TOKENS_LIFETIME])
		strict_requests = cfg[cfg.APP_STRICT_REQUESTS]
		# Core
		password_hasher = argon2.PasswordHasher()
		database = RDatabase.get()

		# Models
		m_rooms_bans	= models.rooms_bans.	RoomsBans(database)
		m_rooms_users	= models.rooms_users.	RoomsUsers(database)
		m_posts			= models.posts.			Posts(database)
		m_rooms			= models.rooms.			Rooms(database, m_rooms_users, m_rooms_bans, m_posts)
		m_users_bans	= models.users_bans.	UsersBans(database)
		m_users			= models.users.			Users(database, m_users_bans, m_rooms, m_rooms_users, m_rooms_bans, m_posts)
		# Services
		s_users			= services.users.		Users(m_users, public_key, tokens_lifetime)
		s_request		= services.request.		Request(s_users, strict_requests)
		s_auth			= services.auth.		Auth()
		# Controllers
		c_login			= controllers.login.		Login(m_users, m_users_bans, s_auth, password_hasher, private_key, strict_requests)
		c_users			= controllers.users.		Users(m_users, m_users_bans, s_auth, password_hasher, strict_requests)
		c_users_bans	= controllers.users_bans.	UsersBans(m_users_bans, s_auth, strict_requests)
		c_rooms			= controllers.rooms.		Rooms(m_rooms, m_rooms_bans, m_rooms_users, s_auth, strict_requests)
		c_rooms_bans	= controllers.rooms_bans.	RoomsBans(m_rooms_bans, m_rooms, m_rooms_users, s_auth, strict_requests)
		c_rooms_users	= controllers.rooms_users.	RoomsUsers(m_rooms_users, m_rooms, m_rooms_bans, s_auth, strict_requests)
		c_posts			= controllers.posts.		Posts(m_posts, m_rooms, m_rooms_users, m_rooms_bans, s_auth, strict_requests)
		# App
		app = flask.Flask(__name__)
		CORS(app)
		if __name__ == '__main__':
			app.json_encoder = main.AppJsonEncoder
		# noinspection PyProtectedMember,PyTypeChecker
		app._register_error_handler(None, werkzeug.exceptions.HTTPException, main.handle_exception)
		# Set up routes
		app.register_blueprint(routes.routes.init(s_request, c_login, c_users, c_users_bans, c_rooms, c_rooms_bans, c_rooms_users, c_posts))
		# Start the app

		self._app_thread = threading.Thread(target=app.run, kwargs={"port": cfg[cfg.APP_PORT], "debug": cfg[cfg.APP_DEBUG], "threaded": False})
		self._app_thread.start()

	def stop(self):
		# can't, apparently
		pass


# noinspection PyMethodMayBeStatic
class RUsers:
	@staticmethod
	def get_token(user_creds: dict) -> str:
		response: requests.Response = requests.post(SERVER_ADDRESS+"/login", json=user_creds)
		assert(response.status_code == HTTPStatus.OK)
		response_dict = json.loads(response.content)
		return response_dict["token"]

	@staticmethod
	def get_user_id_from_token(token: str) -> int:
		try:
			# noinspection PyProtectedMember
			return core.auth.jwt.Token.from_string(token)._payload.claims.user_id
		except core.auth.jwt.Error as jwtError:
			print(jwtError.errors)
			raise jwtError

	@staticmethod
	def get_user_id(user_creds: dict) -> int:
		return RUsers.get_user_id_from_token(RUsers.get_token(user_creds))
