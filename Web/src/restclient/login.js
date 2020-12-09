import Client from "@/restclient/client"

const END_POINT = "/login"

export default class Login {
	static login(login, password) {
		return  Client.Api().post(END_POINT, {login, password})
	}
}
