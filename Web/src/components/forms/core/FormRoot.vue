<template>
	<b-card :title="title" class="w-75 text-center p-0" style="max-width: 420px;">
		<b-form @submit.prevent="submit">
			<slot/>
			<b-button type="submit" style="margin-top: 1vh">{{submitText}}</b-button>
		</b-form>
	</b-card>
</template>

<script>
	export default {
		name: "FormRoot",
		props: {
			"title": String,
			"submitText": String,
			"submitted": Function
		},
		methods: {
			submit: function() {
				this.submitted();
			}
		}
	}
</script>

<style scoped>

</style>