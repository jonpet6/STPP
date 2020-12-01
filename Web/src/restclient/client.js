import axios from 'axios';
// import {Users as api_Users} from "@/restclient/users";

export class Client {
	static _Api = axios.create({
		baseURL: "http://127.0.0.1:4200",
		timeout: 2000,
		headers: {
			"Content-Type": "application/json"
		}
	})

	static Api() {
		if( this._Api.defaults.headers.common["token"] === undefined
			&& localStorage.getItem("token") !== null) {
			this._Api.defaults.headers.common["token"] = localStorage.getItem("token")
		}
		return this._Api;
	}

	static login(token, user) {
		this._Api.defaults.headers.common["token"] = token;
		localStorage.setItem("token", token)
		localStorage.setItem("user", JSON.stringify(user))
	}

	static logout() {
		localStorage.removeItem("token")
		localStorage.removeItem("user")
		delete this._Api.defaults.headers.common["token"];
	}

	static get_user() {
		let user = localStorage.getItem("user")
		if (user === undefined) {
			return null;
		} else {
			return JSON.parse(user)
		}
	}

	static is_logged_in() {
		return this.get_user() !== null;
	}

	static get_user_id_from_token(token) {
		return JSON.parse(atob(token.split(".")[1]))["claims"]["user_id"]
	}
}