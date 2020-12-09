<template>
	<FormRoot title="Register" submit-text="Register" :submitted="submitted">
		<FormInput ref="name" type="text" placeholder="Name" :required="true" icon="person-fill"/>
		<FormInput ref="login" type="text" placeholder="Login" :required="true" icon="key"/>
		<FormInput ref="password" type="password" placeholder="Password" :required="true" icon="lock-fill" />
	</FormRoot>
</template>

<script>
	import api_Users from "@/restclient/users"
	import FormRoot from "@/components/forms/core/FormRoot"
	import FormInput from "@/components/forms/core/inputs/FormInput"

	export default {
		name: "Register",
		props: {
			registeredEvent: Function
		},
		components: {
			FormInput,
			FormRoot
		},
		methods: {
			submitted() {
				api_Users
					.post(this.$refs.name.value, this.$refs.login.value, this.$refs.password.value)
					.then( response => { this.handleResponse(response) })
					.catch( error => { this.handleResponse(error.response) })
			},
			handleResponse(response) {
				console.log(response)
				if (response.status === 201) {
					this.errorsClear()
					this.registered()
				} else {
					this.errorsSet(response.response.data.errors)
				}
			},
			errorsClear() {
				this.$refs.name.errors = null
				this.$refs.login.errors = null
				this.$refs.password.errors = null
			},
			errorsSet(errors) {
				this.$refs.name.errors = errors.keys.name;
				this.$refs.login.errors = errors.keys.login;
				this.$refs.password.errors = errors.keys.password;
			},

			registered() {
				if(this.registeredEvent != null) {
					this.registeredEvent();
				} else {
					this.$router.push("/login")
					location.reload()
				}
			}
		}
	}
</script>

<style scoped>

</style>