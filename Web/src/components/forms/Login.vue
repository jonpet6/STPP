<template>
	<FormRoot title="Login" submitText="Login" :submitted="login">
		<div class="d-flex justify-content-end">
			<p>Or</p>
			<span style="padding-left: 0.2em"></span>
			<b-link v-on:click="register">register</b-link>
		</div>
		<FormGroup ref="group">
			<FormInput ref="login" type="text" placeholder="Login" :required="true" icon="key"/>
			<FormInput ref="password" type="password" placeholder="Password" :required="true" icon="lock-fill"/>
		</FormGroup>
	</FormRoot>
</template>

<script>
	import Client from "@/restclient/client"
	import api_Login from "@/restclient/login"
	import api_Users from "@/restclient/users"
	import FormInput from "@/components/forms/core/inputs/FormInput"
	import FormGroup from "@/components/forms/core/FormGroup"
	import FormRoot from "@/components/forms/core/FormRoot"

	export default {
		name: "Login",
		props: {
			loggedInEvent: Function
		},
		components: {
			FormRoot,
			FormInput,
			FormGroup
		},
		methods: {
			register() {
				this.$router.push('/register')
			},
			errorsClear() {
				this.$refs.group.errors = null
				this.$refs.login.errors = null
				this.$refs.password.errors = null
			},
			errorsSet(errors) {
				this.$refs.group.errors = errors.all;
				if(errors.keys) {
					this.$refs.login.errors = errors.keys.login;
					this.$refs.password.errors = errors.keys.password;
				}
			},
			login() {
				Client.logout()
				api_Login
					.login(this.$refs.login.value, this.$refs.password.value)
					.then( response => { this.loginResponse(response); })
					.catch( error => { this.loginResponse(error.response); })
			},
			loginResponse(response) {
				if( response.status !== 200 ) {
					this.errorsSet(response.data.errors);
				} else  {
					let token = response.data["token"];
					let token_user_id = Client.get_user_id_from_token(token)

					api_Users
						.id_get( token_user_id )
						.then(response => { this.getUserResponse(token, response) })
						.catch(error => { this.getUserResponse(token, error) })
				}
			},
			getUserResponse(token, response) {
				if( response.status !== 200 ) {
					this.errorsSet(response.data.errors);
				} else {
					console.log(response.data)
					console.log(response.data["name"])

					Client.login(token, response.data)

					this.loggedIn();
				}
			},
			loggedIn() {
				if(this.loggedInEvent != null) {
					this.loggedInEvent();
				} else {
					this.$router.push("/")
					location.reload()
				}
			}
		}
	}
</script>

<style scoped>

</style>