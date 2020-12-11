<template>
	<footer style="text-align: center">
		<h1 v-on:click="this.titleClicked">Kaunas 2020</h1>
	</footer>
</template>

<script>
	export default {
		name: "Footer",
		methods: {
			titleClicked() {
				this.$router.push("/users")
			}
		}
	}
</script>

<style scoped>
</style>