<template>
	<b-container id="app" class="h-100 d-flex flex-column">
		<b-row>
			<b-col>
				<MyHeader id="header"/>
			</b-col>
		</b-row>
		<b-row class="flex-fill" align-v="center">
			<b-col>
					<router-view style="margin: auto"/>
			</b-col>
		</b-row>
		<b-row style="display: flex">
			<b-col>
				<Footer id="footer"/>
			</b-col>
		</b-row>
	</b-container>
</template>

<script>
	import MyHeader from "@/components/root/Header";
	import Footer from '@/components/root/Footer'

	export default {
		name: 'App',
		components: {
			MyHeader,
			Footer
		}
	}
</script>

<style>
	html, body {
		height: 100%;
	}
</style>
