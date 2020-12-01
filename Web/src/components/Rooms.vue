<template>
	<ul class="d-flex justify-content-center flex-wrap">
		<Room
			class="m-2 flex-fill"
			style="max-width: 420px"
			v-for="room in rooms" v-bind:key="room['id']"
			v-on:click.native="roomSelected(room)"
			:id="room.id" :user_id="room.user_id"
			:date_created="new Date(Date.parse(room.date_created))"
			:title="room.title" :is_public="room.is_public"
		/>
		<RoomForm
				:room-created-event="refreshRooms"
		/>
	</ul>
</template>

<script>
	import {Rooms as api_Rooms} from "@/restclient/rooms";
	import Room from "@/components/items/Room";
	import RoomForm from "@/components/forms/Room"

	export default {
		name: "Rooms",
		components: {Room, RoomForm},
		mounted() {
			this.getRooms();
		},
		data() { return {
			rooms: [],
		}},
		methods: {
			getRooms() {
				api_Rooms.get()
						.then(response => this.getRoomsResponse(response))
						.catch(error => this.getRoomsResponse(error))
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