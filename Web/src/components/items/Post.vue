<template>
	<f_Post v-if="is_updating"
			:post_id="id" :content="content"
			:room_id="room_id"
			:post-updated-event="this.postUpdated"
	/>
	<LRCard	v-else
			class="w-100"
			:left="username" :left-clicked-event="this.usernameClicked"
			:right="date_created.toLocaleString()"
	>
		<p class="text-left">
			{{content}}
		</p>
		<b-button	v-if="is_owned_by_user"
					class="btn-info" style="float: right"
					v-on:click="this.editClicked">
			<b-icon-pencil-square/> Edit
		</b-button>
	</LRCard>
</template>

<script>
	import api_users from "@/restclient/users"
	import LRCard from "@/components/utils/LRCard"
	import Client from "@/restclient/client"
	import f_Post from "@/components/forms/Post"

	export default {
		name: "Post",
		components: {LRCard, f_Post},
		props: {
			id: Number,
			user_id: Number,
			room_id: Number,
			date_created: Date,
			date_updated: Date,
			content: String,
			postUpdatedEvent: Function,
		},
		data() { return {
			user: "",
			is_updating: false
		}},
		computed: {
			is_owned_by_user() { return this.user !== null && this.user.id === Client.get_user_id() },
			username() { return this.user === null ? "" : this.user.name }
		},
		mounted() {
			this.getUser();
		},
		methods: {
			getUser() {
				api_users.id_get(this.user_id)
					.then(response => this.getUserResponse(response))
					.catch(error => this.getUserResponse(error))
			},
			getUserResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.user = response.data;
				}
			},

			usernameClicked() {
				this.$router.push("/users/"+this.user.id)
			},
			editClicked() {
				this.is_updating = true;
			},
			postUpdated() {
				this.is_updating = false;
				if(this.postUpdatedEvent != null) {
					this.postUpdatedEvent();
				}
			},
		}
	}
</script>

<style scoped>

</style>