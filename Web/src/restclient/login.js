import {Client} from '@/restclient/client'
const END_POINT = "/login"

export class Login {
	static login(login, password) {
		return  Client.Api().post(END_POINT, {login, password})
	}
}
