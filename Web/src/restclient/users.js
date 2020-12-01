import {Client} from '@/restclient/client'

const END_POINT = "/users"

export class Users {
	static get() {
		return Client.Api().get(END_POINT);
	}
	static post(name, login, password) {
		return Client.Api().post(END_POINT,{name, login, password})
	}
	static delete() {
		return Client.Api().delete(END_POINT)
	}

	static id_get(user_id) {
		return Client.Api().get(`${END_POINT}/${user_id}`);
	}
	static id_patch(user_id, data) {
		return Client.Api().patch(`${END_POINT}/${user_id}`, data)
	}
	static id_delete(user_id) {
		return Client.Api().delete(`${END_POINT}/${user_id}`);
	}

	static id_rooms_get(user_id) {
		return Client.Api().get(`${END_POINT}/${user_id}/rooms`)
	}
	static id_rooms_id_get(user_id, room_id) {
		return Client.Api().get(`${END_POINT}/${user_id}/rooms/${room_id}`)
	}
	static id_rooms_id_patch(user_id, room_id, data) {
		return Client.Api().patch(`${END_POINT}/${user_id}/rooms/${room_id}`, data)
	}
	static id_rooms_id_delete(user_id, room_id) {
		return Client.Api().delete(`${END_POINT}/${user_id}/rooms/${room_id}`)
	}

	static id_posts_get(user_id) {
		return Client.Api().get(`${END_POINT}/${user_id}/posts`)
	}
	static id_posts_id_get(user_id, post_id) {
		return Client.Api().get(`${END_POINT}/${user_id}/posts/${post_id}`)
	}
	static id_posts_id_patch(user_id, post_id, data) {
		return Client.Api().patch(`${END_POINT}/${user_id}/posts/${post_id}`, data)
	}
	static id_posts_id_delete(user_id, post_id) {
		return Client.Api().delete(`${END_POINT}/${user_id}/posts/${post_id}`)
	}

	static bans_get() {
		return Client.Api().get(`${END_POINT}/bans`)
	}
	static bans_id_get(user_id) {
		return Client.Api().get(`${END_POINT}/bans/${user_id}`)
	}
	static bans_id_post(user_id, data) {
		return Client.Api().post(`${END_POINT}/bans/${user_id}`, data)
	}
	static bans_id_patch(user_id, data) {
		return Client.Api().patch(`${END_POINT}/bans/${user_id}`, data)
	}
	static bans_id_delete(user_id) {
		return Client.Api().delete(`${END_POINT}/bans/${user_id}`)
	}
}
