<template>
	<b-card class="p-0 m-0">
		<b-form v-on:submit.prevent="submit">

			<b-row class="m-0 p-0 d-flex justify-content-between align-items-end">
				<ToggleButton
						ref="is_public"
						text-on="Public"
						text-off="Private"
						color-on="#889988"
						color-off="#998888"
				/>

				<span style="padding-left: 2vw;"/>
				<p class="h6">Now</p>
			</b-row>

			<b-row class="mt-3">
				<b-col class="justify-content-center text-center">
					<FormInput
							ref="title"
							type="text"
							placeholder="Title"
					/>

					<b-button
							class="w-75" style="margin-top: 1vh"
							type="submit"
					>Create</b-button>
				</b-col>
			</b-row>
		</b-form>
	</b-card>
</template>

<script>
	import FormInput from "@/components/forms/core/inputs/FormInput"
	import ToggleButton from "@/components/forms/core/inputs/ToggleButton"
	import api_Rooms from "@/restclient/rooms"

	export default {
		name: "Room",
		props: {
			roomCreatedEvent: Function
		},
		components: {ToggleButton, FormInput},
		methods: {
			errorsClear() {
				this.$refs.is_public.errors = null
				this.$refs.title.errors = null
			},
			errorsSet(errors) {
				if(errors.keys) {
					this.$refs.is_public.errors = errors.keys.is_public;
					this.$refs.title.errors = errors.keys.title;
				}
			},
			submit() {
				api_Rooms
					.post({title: this.$refs.title.value, is_public: this.$refs.is_public.value})
					.then(response => this.submitReceived(response))
					.catch(error => this.submitReceived(error.response));
			},
			submitReceived(response) {
				if (response.status !== 201) {
					this.errorsSet(response.data.errors)
				} else {
					this.room_created()
				}
			},
			room_created() {
				this.$refs.title.value = ""
				this.$refs.is_public.value = false
				if (this.roomCreatedEvent != null) {
					this.roomCreatedEvent();
				}
			}
		}
	}
</script>

<style scoped>

</style>