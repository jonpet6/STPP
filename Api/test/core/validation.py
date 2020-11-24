from app.core import validation


def main():
	validator = validation.Dict(
		{
			"keyInt": validation.Integer(True, 0, 10),
			"keyString": validation.String(True, 0, 10),
			"keyInt2": validation.Integer(False, 0, 10)
		},
		False, False, False, False
	)
	print("None")
	test(validator, None)

	print("Empty")
	test(validator, {})

	print("Missing keys")
	test(validator, {"keyString": "lol"})

	print("All defined keys missing")
	test(validator, {"lol": "lol"})


def test(validator, dict):
	try:
		validator.validate(dict)
		print("Valid")
	except validation.Error as ve:
		print(ve.errors)


if __name__ == "__main__":
	main()