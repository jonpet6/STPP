import {Client} from '@/restclient/client'

const END_POINT = "/rooms"

export class Rooms {
	static get() {
		return Client.Api().get(END_POINT);
	}
	static post(data) {
		return Client.Api().post(END_POINT, data)
	}

	static id_get(room_id) {
		return Client.Api().get(`${END_POINT}/${room_id}`);
	}
	static id_patch(room_id, data) {
		return Client.Api().patch(`${END_POINT}/${room_id}`, data)
	}
	static id_delete(room_id) {
		return Client.Api().delete(`${END_POINT}/${room_id}`);
	}

	static id_users_get(room_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/users`)
	}
	static id_users_post(room_id, data) {
		return Client.Api().post(`${END_POINT}/${room_id}/users`, data)
	}
	static id_users_id_get(room_id, user_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/users/${user_id}`)
	}
	static id_users_id_delete(room_id, user_id) {
		return Client.Api().delete(`${END_POINT}/${room_id}/users/${user_id}`)
	}
	static id_users_id_posts_get(room_id, user_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/users/${user_id}/posts`)
	}
	static id_users_id_posts_id_get(room_id, user_id, post_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/users/${user_id}/posts/${post_id}`)
	}
	static id_users_id_posts_id_patch(room_id, user_id, post_id, data) {
		return Client.Api().patch(`${END_POINT}/${room_id}/users/${user_id}/posts/${post_id}`, data)
	}
	static id_users_id_posts_id_delete(room_id, user_id, post_id) {
		return Client.Api().delete(`${END_POINT}/${room_id}/users/${user_id}/posts/${post_id}`)
	}

	static id_posts_get(room_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/posts`)
	}
	static id_posts_post(room_id, data) {
		return Client.Api().post(`${END_POINT}/${room_id}/posts`, data)
	}
	static id_posts_id_get(room_id, post_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/posts/${post_id}`)
	}
	static id_posts_id_patch(room_id, post_id, data) {
		return Client.Api().patch(`${END_POINT}/${room_id}/posts/${post_id}`, data)
	}
	static id_posts_id_delete(room_id, post_id) {
		return Client.Api().delete(`${END_POINT}/${room_id}/posts/${post_id}`)
	}

	static id_bans_get(room_id) {
		return Client.Api().get(`${END_POINT}/${room_id}/bans`)
	}
	static id_bans_post(room_id, data) {
		return Client.Api().post(`${END_POINT}/${room_id}/bans`, data)
	}
	static id_bans_patch(room_id, data) {
		return Client.Api().patch(`${END_POINT}/${room_id}/bans`, data)
	}
	static id_bans_delete(room_id) {
		return Client.Api().delete(`${END_POINT}/${room_id}/bans`)
	}
}