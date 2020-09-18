import typing
if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from argon2 import PasswordHasher

import flask
from http import HTTPStatus
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

import utils.responses
from data.orm import Posts
from utils.validation import IntValidator
from utils.validation import StringValidator
from utils.validation import JsonValidator
from utils.validation import ValidationError


def init(database: 'th_Database', pwh: 'PasswordHasher', strict_requests: bool) -> flask.Blueprint:
	bp_posts = flask.Blueprint("bp_posts", __name__)
	#
	# region Posts blueprint
	#

	@bp_posts.route("/posts", methods=["GET"])
	def posts_get():
		return utils.responses.not_implemented()

	@bp_posts.route("/posts", methods=["POST"])
	def posts_post():
		return utils.responses.not_implemented()

	@bp_posts.route("/posts/<id_>", methods=["GET"])
	def posts_id_get(id_: any):
		return utils.responses.not_implemented()

	@bp_posts.route("/posts/<id_>", methods=["PATCH"])
	def posts_id_patch(id_: any):
		return utils.responses.not_implemented()

	@bp_posts.route("/posts/<id_>", methods=["DELETE"])
	def posts_id_delete(id_: any):
		return utils.responses.not_implemented()

	#
	# endregion Posts blueprint
	#
	return bp_posts
