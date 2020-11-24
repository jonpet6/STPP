import typing

if typing.TYPE_CHECKING:
	from core.auth.action import Action as th_Action
	from core.auth.user import User as th_User

from core import responses
from core.auth.user import Registered


class Auth:
	# noinspection PyMethodMayBeStatic
	def authorize(
			self,
			actions: typing.Union['th_Action', typing.List['th_Action']],
			user: 'th_User',
			allowed_ids: typing.Union[int, typing.List[int]] = None
		) -> responses.Response:
		if not isinstance(actions, list):
			actions = [actions]
		# Can the user execute the given actions?
		if all([action in user.role.actions for action in actions]):
			return responses.OKEmpty()
		# The action can now be only executed by allowed user ids
		# Does this user have a user id?
		if not isinstance(user, Registered):
			return responses.UnauthorizedNotLoggedIn()
		# Are there any ids allowed?
		if allowed_ids is not None:
			if not isinstance(allowed_ids, list):
				allowed_ids = [allowed_ids]
			# Is user one of them?
			if user.user_id in allowed_ids:
				return responses.OKEmpty()
		return responses.Forbidden()
