<template>
	<b-input-group>
		<b-input-group-prepend v-if="icon" is-text>
			<b-icon :icon="icon" />
		</b-input-group-prepend>

		<b-form-textarea v-if="type === 'textarea'"
				v-model="value"
				:required="required"
				:placeholder="placeholder"
				:type="type"
				:state="errors == null ? null : false"
		>
			<slot/>
		</b-form-textarea>

		<b-form-input v-else
				v-model="value"
				:required="required"
				:placeholder="placeholder"
				:type="type"
				:state="errors == null ? null : false"
		>
			<slot/>
		</b-form-input>

		<b-form-invalid-feedback v-if="errors">
			{{errors.toString()}}
		</b-form-invalid-feedback>
	</b-input-group>
</template>

<script>
	export default {
		name: "FormInput",
		props: {
			"type": String,
			"placeholder": String,
			"required": Boolean,
			"icon": String
		},
		data: function () {
			return {
				"value": null,
				"errors": null
			}
		}
	}
</script>

<style scoped>

</style>