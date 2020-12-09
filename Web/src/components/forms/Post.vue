<template>
	<LRCard
			left="You"
			right="Now"
	>
		<b-form v-on:submit.prevent="submit">
			<FormInput ref="content" type="textarea" style="word-wrap: normal"></FormInput>
			<b-button
					class="w-25" style="margin-top: 1vh"
					type="submit" >
				<b-icon-pencil-square v-if="is_update"/>
				<b-icon-chat v-else/>

				{{is_update ? "Update" : "Post"}}</b-button>
		</b-form>
	</LRCard>
</template>

<script>
	import api_Rooms from "@/restclient/rooms"
	import LRCard from "@/components/utils/LRCard"
	import FormInput from "@/components/forms/core/inputs/FormInput"

	export default {
		name: "Post",
		props: {
			post_id: Number,
			content: String,

			room_id: Number,
			postCreatedEvent: Function,
			postUpdatedEvent: Function,
		},
		mounted(){
			this.$refs.content.value = this.content;
		},
		components: {FormInput, LRCard},
		computed: {
			is_update() { return this.post_id != null; }
		},
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
				if( this.is_update ) {
					api_Rooms
						.id_posts_id_patch(this.room_id, this.post_id, {content: this.$refs.content.value})
						.then(response => this.updateReceived(response))
						.catch(error => this.updateReceived(error.response));
				} else {
					api_Rooms
						.id_posts_post(this.room_id, {content: this.$refs.content.value})
						.then(response => this.createReceived(response))
						.catch(error => this.createReceived(error.response));
				}
			},
			updateReceived(response) {
				if( response === undefined) {
					return; // no idea why this happens
				}

				if(response.status !== 204) {
					this.errorsSet(response.data.errors)
				} else {
					if(this.postUpdatedEvent != null) {
						this.postUpdatedEvent();
					}
				}
			},
			createReceived(response) {
				if (response.status !== 201) {
					this.errorsSet(response.data.errors)
				} else {
					this.$refs.content.value = ""
					if (this.postCreatedEvent != null) {
						this.postCreatedEvent();
					}
				}
			},
		}
	}
</script>

<style scoped>

</style>