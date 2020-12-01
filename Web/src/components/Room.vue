<template>
	<LRCard
			:left="room.title"
			:right="'Owner: '+username"
	>
		<div class="d-flex justify-content-between align-items-end">
			<p v-for="user in users" v-bind:key="user.id">
				{{user.name}}
			</p>
		</div>

		<Post
			v-for="post in posts" v-bind:key="post.id"
			:id="post.id" :user_id="post.user_id" :room_id="post.room_id"
			:content="post.content"
			:date_created="new Date(Date.parse(post.date_created))"
			:date_updated="new Date(Date.parse(post.date_updated))"
		/>
		<PostForm
				:room_id="room.id"
				:post-created-event="refresh_posts"
		/>
	</LRCard>
</template>

<script>
	import {Rooms as api_Rooms} from "@/restclient/rooms";
	import {Users as api_users} from "@/restclient/users";
	import LRCard from "@/components/utils/LRCard";
	import Post from "@/components/items/Post";
	import PostForm from "@/components/forms/Post"

	export default {
		name: "Room",
		components: {LRCard, Post, PostForm},
		mounted() {
			this.getRoom();
			this.getRUs();
			this.getPosts();
		},
		data() {
			return {
				room: Object,
				users: [],
				posts: Object,

				user: Object,
			}
		},
		computed: {
			username() { return this.user === null ? "" : this.user.name }
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

			refresh_posts() {
				this.getPosts()
			}
		}
	}
</script>

<style scoped>

</style>