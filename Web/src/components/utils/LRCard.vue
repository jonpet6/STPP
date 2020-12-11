<template>
	<b-card class="p-0 m-0">
		<b-row class="d-flex justify-content-between align-items-end m-0 p-0">

			<p class="h4" v-on:click="this.leftClicked">{{left}}</p>

			<span style="padding-left: 2vw;"/>

			<p class="h4" v-on:click="this.centerClicked">{{center}}</p>

			<span style="padding-left: 2vw;"/>

			<p class="h6" v-on:click="this.rightClicked">{{right}}</p>
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
			leftClickedEvent: Function,
			center: String,
			centerClickedEvent: Function,
			right: String,
			rightClickedEvent: Function,
		},
		methods: {
			leftClicked() { if(this.leftClickedEvent != null) { this.leftClickedEvent() } },
			centerClicked() { if(this.centerClickedEvent != null) { this.centerClickedEvent() } },
			rightClicked() { if(this.rightClickedEvent != null) { this.rightClickedEvent() } },
		}
	}
</script>

<style scoped>
</style>