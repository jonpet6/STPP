import Vue from 'vue'
import VueRouter from 'vue-router';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Register from "@/components/forms/Register";
import Login from "@/components/forms/Login";
import App from "@/components/root/App";
import Rooms from "@/components/Rooms";
import Room from "@/components/Room";

Vue.config.productionTip = false

Vue.use(VueRouter)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

const router = new VueRouter({
	mode: 'history',
	routes: [
		{ path: '/login', component: Login},
		{ path: '/register', component: Register},
		{ path: '/', redirect: '/rooms' },
		{ path: '/rooms', component: Rooms},
		{ path: '/rooms/:id', component: Room }
	]
})

new Vue({
	router,
	render: h => h(App)
}).$mount('#app')
