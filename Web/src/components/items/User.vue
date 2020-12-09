<template>
	<LRCard
			:left="this.name"
			:right="'Joined ' + this.date_created.toLocaleDateString()"
	>
		<b-card-sub-title v-if="this.is_admin" class="mt-1">
			Administrator
		</b-card-sub-title>
	</LRCard>
</template>

<script>
	import m_Roles from "@/models/roles"
	import LRCard from "@/components/utils/LRCard";

	export default {
		name: "User",
		components: {LRCard},
		props: {
			id: Number,
			role: Number,
			date_created: Date,
			name: String,
		},
		mounted() {
			this.getUser();
		},
		data() {
			return {
				user: Object,
			}
		},
		computed: {
			is_admin() {
				return this.role === m_Roles.role_to_id(m_Roles.roles.ADMINISTRATOR)
			},
		},
	}
</script>

<style scoped>
</style>
