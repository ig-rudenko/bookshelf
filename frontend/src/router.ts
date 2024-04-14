import {createRouter, createWebHistory, RouteRecordRaw} from "vue-router";

import Login from "@/pages/Login.vue";
import Register from "@/pages/Register.vue";
import Home from "@/pages/Home.vue";
import CreateBook from "@/pages/CreateBook.vue";
import BookPage from "@/pages/BookPage.vue";


const routes: RouteRecordRaw[] = [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/signup", component: Register },
    { path: "/create-book", component: CreateBook },
    { path: "/book/:id", component: BookPage },
]

export default function createAppRouter() {
    return createRouter({
        history: createWebHistory(),
        routes,
    });
}