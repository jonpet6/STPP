<template>
	<ErrorCard v-if="this.error_response !== null" :response="this.error_response"/>
	<LRCard v-else
			:left="room.title"
			:left-clicked-event="roomClicked"
			:right="owner" :right-clicked-event="ownerClicked">

		<LRCard style="border: 0;">
				<b-select v-model="selected_user" style="width: 80%">
					<option disabled :value="null">Select a user</option>
					<option v-for="user in all_users" v-bind:key="user.id" v-bind:value="user">
						{{user.name}}
					</option>
				</b-select>
				<b-button class="btn-info" v-on:click="userAddClicked">
					<b-icon-person-plus/>
					Add
				</b-button>
				<div v-if="this.add_errors.length > 0" ref="errorsFeedback" style="color: red">{{this.add_errors.toString()}}</div>
		</LRCard>

		<div class="d-flex">
			<ul class="list-inline mx-auto justify-content-center">
				<RoomUser class="m-2"
					v-for="user in users" v-bind:key="user.id"
					:user_id="user.id" :name="user.name"
					:allow_remove="true"
					:remove-clicked-event="userRemoveClicked"
				/>
			</ul>
		</div>
	</LRCard>
</template>

<script>
	import api_Rooms from "@/restclient/rooms";
	import api_users from "@/restclient/users";
	import LRCard from "@/components/utils/LRCard";
	import ErrorCard from "@/components/utils/ErrorCard";
	import RoomUser from "@/components/items/RoomUser";

	export default {
		name: "RoomUsers",
		components: {ErrorCard,LRCard,RoomUser},
		data() { return {
			room: Object,
			user: null,
			users: [],

			all_users: [],

			selected_user: null,

			add_errors: [],

			error_response: null
		}},
		computed: {
			owner() { return this.user === null ? "" : "Owner: "+ this.user.name },
			owner_id() { return this.room['user_id']; }
		},
		mounted() {
			this.getRoom();
			this.getRUs();
			this.getAllUsers();
		},
		methods: {
			userRemoveClicked(id) {
				this.removeUser(id)
			},
			removeUser(user_id) {
				api_Rooms.id_users_id_delete(this.$route.params.id, user_id)
					.then(response => this.removeUserReceived(response))
					.catch(error => this.removeUserReceived(error.response))
			},
			removeUserReceived(response) {
				if( response.status !== 204 ) {
					console.log(response)
				} else {
					this.users = []
					this.getRUs()
				}
			},
			userAddClicked() { this.addUser(this.selected_user.id) },
			addUser(user_id) {
				api_Rooms
					.id_users_post(this.$route.params.id, {"user_id": user_id})
					.then(response => this.addUserReceived(response))
					.catch(error => this.addUserReceived(error.response))
			},
			addUserReceived(response) {
				if( response.status !== 201) {
					console.log(response)
					this.add_errors = response.data.errors
				} else {
					this.users = []
					this.getRUs()
				}
			},
			getRoom() {
				api_Rooms.id_get(this.$route.params.id)
					.then(response => this.getRoomResponse(response))
					.catch(error => this.getRoomResponse(error.response))
			},
			getRoomResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
					this.error_response = response
				} else {
					this.room = response.data;
					this.getUser(this.room["user_id"]);
				}
			},
			getRUs() {
				api_Rooms.id_users_get(this.$route.params.id)
					.then(response => this.getRUsResponse(response))
					.catch(error => this.getRUsResponse(error.response))
			},
			getRUsResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					response.data.forEach( ru => this.getRUasUser(ru.user_id) )
				}
			},
			getRUasUser(user_id) {
				api_users.id_get(user_id)
					.then(response => this.getRUasUserResponse(response))
					.catch(error => this.getRUasUserResponse(error.response))
			},
			getRUasUserResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.users.push(response.data)
				}
			},
			getUser(user_id) {
				api_users.id_get(user_id)
					.then(response => this.getUserResponse(response))
					.catch(error => this.getUserResponse(error.response))
			},
			getUserResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.user = response.data;
				}
			},
			getAllUsers() {
				api_users.get()
					.then(response => this.getAllUsersResponse(response))
					.catch(error => this.getAllUsersResponse(error.response))
			},
			getAllUsersResponse(response) {
				if( response === undefined ) { return }
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.all_users = response.data;
				}
			},
			ownerClicked() {
				this.$router.push("/users/"+this.user.id)
			},
			roomClicked() {
				this.$router.push("/rooms/"+this.$route.params.id)
			}
		}
	}
</script>

<style scoped>

</style>