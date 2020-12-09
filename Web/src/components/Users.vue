<template>
	<ul class="d-flex justify-content-center flex-wrap flex-column">
		<div class="d-flex">
			<ul class="list-inline mx-auto justify-content-center">
				<User
						class="m-2 flex-fill"
						style="max-width: 420px"

						v-for="user in users" v-bind:key="user['id']"
						v-on:click.native="userSelected(user)"

						:id="user.id" :role="user.role"
						:name="user.name" :date_created="new Date(Date.parse(user.date_created))"
				/>
			</ul>
		</div>
	</ul>
</template>

<script>
	import api_Users from "@/restclient/users"
	import User from "@/components/items/User";

	export default {
		name: "Users",
		components: {User},
		data() { return {
			users: []
		}},
		mounted() {
			this.getUsers();
		},
		methods: {
			getUsers() {
				api_Users.get()
					.then(response => this.getUsersResponse(response))
					.catch(error => this.getUsersResponse(error.response))
			},
			getUsersResponse(response) {
				if( response.status !== 200 ) {
					console.log(response)
				} else {
					this.users = response.data;
				}
			},

			userSelected(user) {
				this.$router.push("/users/"+user.id);
			},
			refreshUsers() {
				this.getUsers();
			}
		}
	}
</script>

<style scoped>

</style>