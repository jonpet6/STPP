<template>
	<LRCard class="alert-danger"
		:left="this.title"
		:right="this.response.status">
		<Json
			:data="response.data.errors"
		/>
	</LRCard>
</template>

<script>
	import LRCard from "@/components/utils/LRCard";
	import Json from "@/components/utils/Json";

	export default {
		name: "ErrorCard",
		components: {LRCard, Json},
		props: {
			"response": Object
		},
		computed: {
			title() {
				return "Error" + (this.response !== null ?  ": " + this.response.statusText.toLowerCase() : "")
			}
		}
	}
</script>

<style scoped>

</style>