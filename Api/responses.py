import flask


def return_error(errors: str or [str], http_code: int):
	if type(errors) is not list:
		errors = [errors]

	return flask.jsonify({
		"errors": errors
	}), http_code
