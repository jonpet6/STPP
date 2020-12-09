<template>
	<b-card style="border: 0">
		<pre style="text-align: left;">
			{{display}}
		</pre>
	</b-card>
</template>

<script>
	export default {
		name: "Json",
		props: {
			"data": {}
		},
		computed: {
			display() {
				return '\n'+JSON.stringify(this.data, null, 4);
			}
		}
	}
</script>

<style scoped>

</style>