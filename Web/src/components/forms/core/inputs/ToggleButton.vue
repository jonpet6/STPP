<template>
	<div>
		<b-button
				:style="'background-color: '+this.color"
				v-on:click="clicked"
		>
			{{text}}
		</b-button>
		<b-form-invalid-feedback v-if="errors">
			{{errors.toString()}}
		</b-form-invalid-feedback>
	</div>
</template>

<script>
	export default {
		name: "ToggleButton",
		props: {
			"textOn": String,
			"textOff": String,
			"colorOn": String,
			"colorOff": String,
		},
		data: function () {
			return {
				"value": false,
				"errors": null,
			}
		},
		computed: {
			text() {
				return this.value ? this.textOn : this.textOff;
			},
			color() {
				return this.value ? this.colorOn : this.colorOff;
			}
		},
		methods: {
			clicked() {
				this.value = !this.value;
			}
		}
	}
</script>

<style scoped>

</style>