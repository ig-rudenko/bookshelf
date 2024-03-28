import {createRouter, createWebHistory, RouteRecordRaw} from "vue-router";

import Login from "./pages/Login.vue";
import Home from "./pages/Home.vue";


const routes: RouteRecordRaw[] = [
    { path: "/", component: Home },
    { path: "/login", component: Login },
]

export default function createAppRouter() {
    return createRouter({
        history: createWebHistory(),
        routes,
    });
}