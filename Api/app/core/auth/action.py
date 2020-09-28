from enum import Enum, auto


class Action(Enum):
	# Login
	LOGIN = auto()
	# Users
	USERS_CREATE = auto()
	USERS_GET = auto()
	USERS_GET_ALL = auto()
	USERS_UPDATE = auto()
	USERS_UPDATE_NAME = auto()
	USERS_UPDATE_ROLE = auto()
	USERS_UPDATE_CREDENTIALS = auto()
	USERS_DELETE = auto()
	# Users bans
	USERS_BANS_CREATE = auto()
	USERS_BANS_GET = auto()
	USERS_BANS_GET_ALL = auto()
	USERS_BANS_GET_ALL_VISIBLE = auto()
	USERS_BANS_UPDATE = auto()
	USERS_BANS_DELETE = auto()
	# Rooms
	ROOMS_CREATE = auto()
	ROOMS_GET = auto()
	ROOMS_GET_VISIBLE = auto()
	ROOMS_GET_PUBLIC = auto()
	ROOMS_GET_ALL = auto()
	ROOMS_GET_ALL_VISIBLE = auto()
	ROOMS_UPDATE = auto()
	ROOMS_DELETE = auto()
	# Rooms users
	ROOMS_USERS_CREATE = auto()
	ROOMS_USERS_GET = auto()
	ROOMS_USERS_GET_ALL = auto()
	ROOMS_USERS_GET_VISIBLE = auto()
	ROOMS_USERS_DELETE = auto()
	# Rooms bans
	ROOMS_BANS_CREATE = auto()
	ROOMS_BANS_GET = auto()
	ROOMS_BANS_GET_ALL = auto()
	ROOMS_BANS_GET_ALL_VISIBLE = auto()
	ROOMS_BANS_UPDATE = auto()
	ROOMS_BANS_DELETE = auto()
	# Posts
	POSTS_CREATE = auto()
	POSTS_CREATE_PRIVATE = auto()
	POSTS_CREATE_PUBLIC = auto()
	POSTS_GET = auto()
	POSTS_GET_ALL = auto()
	POSTS_GET_ALL_VISIBLE = auto()
	POSTS_UPDATE = auto()
	POSTS_DELETE = auto()
