<template>

	<ErrorCard v-if="this.error_response !== null" :response="this.error_response"/>
	<LRCard v-else
		:left="this.user.name"
	>
		<LRCard :v-if="this.userHasRooms"  center="User's rooms" style="border: none">
			<ul class="list-inline d-flex justify-content-center">
				<Room
						class="m-2 flex-fill"
						style="max-width: 420px"

						v-for="room in this.rooms" v-bind:key="room['id']"
						v-on:click.native="roomSelected(room)"

						:id="room.id" :user_id="room.user_id"
						:date_created="new Date(Date.parse(room.date_created))"
						:title="room.title" :is_public="room.is_public"
				/>
			</ul>
		</LRCard>
	</LRCard>
</template>

<script>
	import api_Users from "@/restclient/users"
	import Room from "@/components/items/Room";
	import LRCard from "@/components/utils/LRCard";
	import ErrorCard from "@/components/utils/ErrorCard";

	export default {
		name: "User",
		components: {ErrorCard, LRCard, Room},
		data() { return {
			user: Object,
			rooms: [],
			error_response: null,
		}},
		mounted() {
			this.getUser();
		},
		computed: {
			userHasRooms() {
				return this.rooms !== null && this.rooms.length > 1
			}
		},
		methods: {
			getUser() {
				api_Users.id_get(this.$route.params.id)
					.then(response => this.getUserResponse(response))
					.catch(error => this.getUserResponse(error.response))
			},
			getUserResponse(response) {
				if( response.status !== 200 ) {
					this.error_response = response;
					console.log(response)
				} else {
					this.user = response.data;
					this.getRooms(this.user.id)
				}
			},
			getRooms(user_id) {
				api_Users.id_rooms_get(user_id)
					.then(response => this.getRoomsResponse(response))
					.catch(error => this.getRoomsResponse(error.response))
			},
			getRoomsResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.rooms = response.data;
				}
			},

			roomSelected(room) {
				this.$router.push("/rooms/"+room.id);
			},
		}
	}
</script>

<style scoped>
</style>
