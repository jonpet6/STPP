from enum import Enum, auto


class Action(Enum):
	LOGIN = auto()

	# Users
	USERS_CREATE = auto()
	USERS_UPDATE_NAME = auto()
	USERS_UPDATE_ROLE = auto()
	USERS_UPDATE_CRED = auto()
	USERS_DELETE = auto()
	USERS_DELETE_SELF = auto()
	# Users bans
	USERS_BANS_CREATE = auto()
	USERS_BANS_UPDATE = auto()
	USERS_BANS_DELETE = auto()
	# Rooms
	ROOMS_CREATE = auto()
	ROOMS_UPDATE_TITLE = auto()
	ROOMS_DELETE = auto()
	# Rooms bans
	ROOMS_BANS_CREATE = auto()
	ROOMS_BANS_UPDATE = auto()
	ROOMS_BANS_DELETE = auto()
	# Rooms users
	ROOMS_USERS_CREATE = auto()
	ROOMS_USERS_DELETE = auto()
	# Posts
	POSTS_CREATE = auto()
	POSTS_CREATE_PUBLIC = auto()
	POSTS_UPDATE = auto()
	POSTS_CLEAR = auto()
	POSTS_DELETE = auto()

	# Access
	USERS_ACCESS_NOTBANNED = auto()
	USERS_ACCESS_BANNED = auto()

	ROOMS_ACCESS_PUBLIC = auto()
	ROOMS_ACCESS_PRIVATE = auto()
	ROOMS_ACCESS_BANNED = auto()
	ROOMS_BANS_ACCESS = auto()
	ROOMS_USERS_ACCESS = auto()
	ROOMS_POSTS_ACCESS = auto()
