<template>
	<ErrorCard v-if="this.error_response !== null" :response="this.error_response"/>
	<LRCard v-else
			:left="room.title"
			:center=" room.is_public ? '' : '(private)' "
			:right="owner" :right-clicked-event="ownerClicked"
	>
		<div class="d-flex justify-content-between align-items-end pb-2" style="float: right;">
			<div class="list" style="margin: 0 3px;" v-for="user in users" v-bind:key="user.id">
				<RoomUser :name="user.name" :user_id="user.id" :allow_remove="false"/>
			</div>

			<b-button	v-if="is_owned_by_user"
						v-on:click="manageUsersClicked"
						class="btn-info">
				<b-icon-person-lines-fill/> Manage users
			</b-button>
		</div>

		<Post
			v-for="post in posts" v-bind:key="post.id"
			:id="post.id" :user_id="post.user_id" :room_id="post.room_id"
			:content="post.content"
			:date_created="new Date(Date.parse(post.date_created))"
			:date_updated="new Date(Date.parse(post.date_updated))"
			:post-updated-event="refresh_posts"
		/>
		<PostForm v-if="is_logged_in"
				:room_id="room.id"
				:post-created-event="refresh_posts"
		/>
	</LRCard>
</template>

<script>
	import Client from "@/restclient/client"
	import api_Rooms from "@/restclient/rooms"
	import api_users from "@/restclient/users"
	import LRCard from "@/components/utils/LRCard"
	import Post from "@/components/items/Post"
	import PostForm from "@/components/forms/Post"
	import RoomUser from "@/components/items/RoomUser";

	export default {
		name: "Room",
		components: {LRCard, Post, PostForm, RoomUser},
		data() { return {
			room: Object,
			users: [],
			posts: Object,

			user: Object,

			error_response: null
		}},
		computed: {
			is_logged_in() { return Client.is_logged_in() },
			is_owned_by_user() { return this.user !== null && this.user['id'] === Client.get_user_id() },
			owner() { return this.user === null ? "" : "Owner: "+ this.user.name },
		},
		mounted() {
			this.getRoom();
			this.getRUs();
			this.getPosts();
		},
		methods: {
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

			getPosts() {
				api_Rooms.id_posts_get(this.$route.params.id)
					.then(response => this.getPostsReceived(response))
					.catch(error => this.getPostsReceived(error.response))
			},
			getPostsReceived(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.posts = response.data;
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

			ownerClicked() {
				this.$router.push("/users/"+this.user.id)
			},
			manageUsersClicked() {
				this.$router.push("/rooms/"+this.$route.params.id+"/users")
			},
			refresh_posts() {
				this.getPosts()
			}
		}
	}
</script>

<style scoped>

</style>