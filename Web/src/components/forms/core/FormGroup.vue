<template>
	<b-form-group
			:state="errors == null ? null : false"
			:invalid-feedback="errors == null ? null : errors.toString()"
	>
		<slot/>
	</b-form-group>
</template>

<script>
	export default {
		name: "FormGroup",
		data: function() {
			return {
				errors: null
			}
		},
	}
</script>

<style scoped>

</style>