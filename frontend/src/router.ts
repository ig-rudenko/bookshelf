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
import LastViewed from "@/pages/LastViewed.vue";
import ForgotPassword from "@/pages/ForgotPassword.vue";
import ResetPassword from "@/pages/ResetPassword.vue";
import Bookshelves from "@/pages/Bookshelves.vue";
import CreateUpdateBookshelf from "@/pages/CreateUpdateBookshelf.vue";


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
    { path: "/forgot-password", component: ForgotPassword },
    { path: "/reset-password/:token", component: ResetPassword },
    { path: "/favorites", component: Favorites },
    { path: "/read", component: ReadBooks },
    { path: "/last-viewed", component: LastViewed },
    { path: "/create-book", component: CreateBook },
    { path: "/bookshelves", component: Bookshelves },
    { path: "/bookshelves/create", component: CreateUpdateBookshelf },
    { path: "/bookshelves/:id/edit", component: CreateUpdateBookshelf },
    { path: "/book/:id", component: BookPage, beforeEnter: beforeEnter },
    { path: "/book/:id/edit", component: UpdateBook, beforeEnter: beforeEnter },
    { path: "/book/:id/show", component: ShowBook, beforeEnter: beforeEnter },
]

const router: Router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;