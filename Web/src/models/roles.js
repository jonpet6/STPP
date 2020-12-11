
export default class Roles {
	// enum
	static roles = {
		GUEST: -1,
		USER: -2,
		ADMINISTRATOR: -3,
	}
	// Maps a role to an index
	static role_order = [
		this.roles.GUEST,
		this.roles.USER,
		this.roles.ADMINISTRATOR
	]

	static role_to_id(role) {
		return this.role_order.indexOf(role);
	}
	static id_to_role(id) {
		return this.role_order[id];
	}
}