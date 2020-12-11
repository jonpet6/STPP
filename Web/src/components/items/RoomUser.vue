<template>
	<b-card class="m-0 p-1" style="max-width: 160px; max-height: 50px">
		<b-row class="justify-content-between align-self-middle">
			<span class="align-middle">{{name}}</span>
			<b-button	v-if="allow_remove"
						class="btn-danger m-0 align-middle"
						style="max-width: 80px; max-height: 30px; padding: 0 10px 0 10px;"
						v-on:click="removeClicked"
			>
				<b-icon-person-dash/>
			</b-button>
		</b-row>
	</b-card>
</template>

<script>
	export default {
		name: "RoomUser",
		props: {
			user_id: Number,
			name: String,
			allow_remove: Boolean,
			removeClickedEvent: Function[Number]
		},
		methods: {
			removeClicked() {
				if(this.removeClickedEvent !== null ) {
					this.removeClickedEvent(this.user_id)
				}
			}
		}
	}
</script>

<style scoped>
	.card-body {
		padding: 1px 20px;
	}
</style>