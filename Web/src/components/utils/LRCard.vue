<template>
	<b-card class="p-0 m-0">
		<b-row class="d-flex justify-content-between align-items-end m-0 p-0">
			<p class="h4">{{left}}</p>
			<span style="padding-left: 2vw;"/>
			<p class="h6">{{right}}</p>
		</b-row>

		<b-row>
			<b-col class="justify-content-center text-center">
				<slot/>
			</b-col>
		</b-row>
	</b-card>
</template>

<script>
	export default {
		name: "LRCard",
		props: {
			left: String,
			right: String,
		}
	}
</script>

<style scoped>
</style>