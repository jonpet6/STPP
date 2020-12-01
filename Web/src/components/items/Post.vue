<template>
	<LRCard	class="w-100"
			:left="username"
			:right="date_created.toLocaleString()"
	>
		<p class="text-left">
			{{content}}
		</p>
	</LRCard>
</template>

<script>
	import {Users as api_users} from "@/restclient/users";
	import LRCard from "@/components/utils/LRCard";

	export default {
		name: "Post",
		components: {LRCard},
		props: {
			id: Number,
			user_id: Number,
			room_id: Number,
			date_created: Date,
			date_updated: Date,
			content: String,
		},
		data() { return {
			user: ""
		}},
		computed: {
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
			}
		}
	}
</script>

<style scoped>

</style>