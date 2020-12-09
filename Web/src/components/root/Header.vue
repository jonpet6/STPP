<template>
	<header id="header" class="d-flex justify-content-between">
		<h1 v-on:click="home()">STPP</h1>
		<div>
			<div v-if="is_logged_in" class="d-flex flex-md-row">
				<h2 ref="userName" v-on:click="usernameClicked">{{ username }}</h2>

				<span style="padding-left: 1vw;"/>
				<b-button v-on:click="logout" style="margin: auto">Logout</b-button>
			</div>
			<div v-else-if="show_login" class="d-flex flex-md-row">
				<b-button v-on:click="login">Login</b-button>
			</div>
		</div>
	</header>
</template>

<script>
	import Client from "@/restclient/client"

	export default {
		name: "Header",
		computed: {
			username() {
				return Client.get_user() === null ? "ERROR" : Client.get_user().name;
			},
			is_logged_in() {
				return Client.is_logged_in();
			}
		},
		methods: {
			show_login() {
				return this.$route.path !== "/login";
			},
			login() {
				this.$router.push("/login");
			},
			logout() {
				Client.logout();
				location.reload();
			},
			home() {
				this.$router.push("/");
			},
			usernameClicked() {
				let user_id = Client.get_user_id();
				if( user_id != null) {
					this.$router.push("/users/"+user_id)
				}
			}
		}
	}
</script>

<style scoped>
	#header {
		text-align: center;
	}
</style>