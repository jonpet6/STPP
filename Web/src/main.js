import Vue from 'vue'
import VueRouter from 'vue-router';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Register from "@/components/forms/Register"
import Login from "@/components/forms/Login"
import App from "@/components/root/App"
import Users from "@/components/Users"
import User from "@/components/User"
import Rooms from "@/components/Rooms"
import Room from "@/components/Room"
import RoomUsers from "@/components/RoomUsers";

Vue.config.productionTip = false

Vue.use(VueRouter)
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)

const router = new VueRouter({
	mode: 'history',
	routes: [
		{ path: '/login', component: Login },
		{ path: '/register', component: Register },
		{ path: '/', redirect: '/rooms' },
		{ path: '/users', component: Users },
		{ path: '/users/:id', component: User },
		{ path: '/rooms', component: Rooms },
		{ path: '/rooms/:id', component: Room },
		{ path: '/rooms/:id/users', component: RoomUsers }
	]
})

new Vue({
	router,
	render: h => h(App)
}).$mount('#app')
