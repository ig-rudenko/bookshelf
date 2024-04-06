import {createRouter, createWebHistory, RouteRecordRaw} from "vue-router";

import Login from "@/pages/Login.vue";
import Register from "@/pages/Register.vue";
import Home from "@/pages/Home.vue";
import CreateBook from "@/pages/CreateBook.vue";


const routes: RouteRecordRaw[] = [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/signup", component: Register },
    { path: "/create-book", component: CreateBook },
]

export default function createAppRouter() {
    return createRouter({
        history: createWebHistory(),
        routes,
    });
}