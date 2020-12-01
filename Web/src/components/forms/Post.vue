<template>
	<LRCard
			left="You"
			right="Now"
	>
		<b-form v-on:submit.prevent="submit">
			<FormInput ref="content" type="textarea" style="word-wrap: normal"/>
			<b-button
					class="w-25" style="margin-top: 1vh"
					type="submit" >Post</b-button>
		</b-form>
	</LRCard>
</template>

<script>
	import {Rooms as api_Rooms} from "@/restclient/rooms";
	import LRCard from "@/components/utils/LRCard";
	import FormInput from "@/components/forms/core/inputs/FormInput";

	export default {
		name: "Post",
		props: {
			room_id: Number,
			postCreatedEvent: Function
		},
		components: {FormInput, LRCard},
		methods: {
			errorsClear() {
				this.$refs.content.errors = null
			},
			errorsSet(errors) {
				if(errors.keys) {
					this.$refs.content.errors = errors.keys.content;
				}
			},
			submit() {
				api_Rooms
					.id_posts_post(this.room_id, {content: this.$refs.content.value})
					.then(response => this.submitReceived(response))
					.catch(error => this.submitReceived(error.response));
			},
			submitReceived(response) {
				if (response.status !== 201) {
					this.errorsSet(response.data.errors)
				} else {
					this.post_created()
				}
			},
			post_created() {
				this.$refs.content.value = ""
				if (this.postCreatedEvent != null) {
					this.postCreatedEvent();
				}
			}
		}
	}
</script>

<style scoped>

</style>