<template>
	<div>
		<ul class="d-flex justify-content-center flex-wrap" style="list-style-type: none">
			<Room
				class="m-2 flex-fill"
				style="max-width: 420px"

				v-for="room in rooms" v-bind:key="room['id']"
				v-on:click.native="roomSelected(room)"

				:id="room.id" :user_id="room.user_id"
				:date_created="new Date(Date.parse(room.date_created))"
				:title="room.title" :is_public="room.is_public"
			/>

			<li class="flex-fill" style="height: 0; width: 100%; flex-basis: 100%"/>

			<RoomForm v-if="is_logged_in"
					class="m-2 flex-fill"
					style="max-width: 420px"
					:room-created-event="refreshRooms"
			/>
		</ul>
	</div>
</template>

<script>
	import api_Rooms from "@/restclient/rooms"
	import Room from "@/components/items/Room"
	import RoomForm from "@/components/forms/Room"
	import Client from "@/restclient/client"

	export default {
		name: "Rooms",
		components: {Room, RoomForm},
		data() { return {
			rooms: [],
		}},
		mounted() {
			this.getRooms();
		},
		computed: {
			is_logged_in() { return Client.is_logged_in(); }
		},
		methods: {
			getRooms() {
				api_Rooms.get()
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
			refreshRooms() {
				this.getRooms();
			}
		}
	}
</script>

<style scoped>

</style>