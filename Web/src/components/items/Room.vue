<template>
	<LRCard
		:left="is_public ? 'Public' : 'Private'"
		:right="date_created.toLocaleString()"
	>
		<p class="h1">{{title}}</p>
	</LRCard>
</template>

<script>
	import LRCard from "@/components/utils/LRCard"

	export default {
		name: "Room",
		components: {LRCard},
		props: {
			id: Number,
			user_id: Number,
			date_created: Date,
			is_public: Boolean,
			title: String,
		}
	}
</script>

<style scoped>
</style>