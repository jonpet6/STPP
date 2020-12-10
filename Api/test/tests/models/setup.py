import test.resources.common
from app.models.posts import Posts
from app.models.rooms import Rooms
from app.models.rooms_bans import RoomsBans
from app.models.rooms_users import RoomsUsers
from app.models.users import Users
from models.users_bans import UsersBans

from test.resources import reset

reset.reset_database()

database = test.resources.common.RDatabase.get()
m_posts = Posts(database)
m_rooms_users = RoomsUsers(database)
m_rooms_bans = RoomsBans(database)
m_rooms = Rooms(database, m_rooms_users, m_rooms_bans, m_posts)
m_users_bans = UsersBans(database)
m_users = Users(database, m_users_bans, m_rooms, m_rooms_users, m_rooms_bans, m_posts)
