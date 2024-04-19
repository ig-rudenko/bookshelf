import {
    createRouter,
    createWebHistory,
    NavigationGuardNext,
    RouteLocationNormalized,
    Router,
    RouteRecordRaw
} from "vue-router";

import Login from "@/pages/Login.vue";
import Register from "@/pages/Register.vue";
import Home from "@/pages/Home.vue";
import CreateBook from "@/pages/CreateBook.vue";
import BookPage from "@/pages/BookPage.vue";
import UpdateBook from "@/pages/UpdateBook.vue";
import ShowBook from "@/pages/ShowBook.vue";
import Favorites from "@/pages/Favorites.vue";
import ReadBooks from "@/pages/ReadBooks.vue";


const beforeEnter = (to: RouteLocationNormalized, _: RouteLocationNormalized, next: NavigationGuardNext) => {
    const id = Number(to.params.id);
    if (!isNaN(id) && Number.isInteger(id)) {
        next();
    } else {
        next({ path: '/' }); // Редирект на главную страницу, если id не числовое
    }
}

const routes: RouteRecordRaw[] = [
    { path: "/", component: Home },
    { path: "/login", component: Login },
    { path: "/signup", component: Register },
    { path: "/favorites", component: Favorites },
    { path: "/read", component: ReadBooks },
    { path: "/create-book", component: CreateBook },
    { path: "/book/:id", component: BookPage, beforeEnter: beforeEnter },
    { path: "/book/:id/edit", component: UpdateBook, beforeEnter: beforeEnter },
    { path: "/book/:id/show", component: ShowBook, beforeEnter: beforeEnter },
]

const router: Router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;