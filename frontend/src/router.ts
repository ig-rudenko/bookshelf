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
import AllUsers from "@/pages/admin/AllUsers.vue";


const beforeEnter = (to: RouteLocationNormalized, _: RouteLocationNormalized, next: NavigationGuardNext) => {
    const id = Number(to.params.id);
    if (!isNaN(id) && Number.isInteger(id)) {
        next();
    } else {
        next({path: '/'}); // Редирект на главную страницу, если id не числовое
    }
}

const routes: RouteRecordRaw[] = [
    {path: "/", component: Home, name: "home"},
    {path: "/login", component: Login, name: "login"},
    {path: "/signup", component: Register, name: "register"},
    {path: "/forgot-password", component: ForgotPassword, name: "forgotPassword"},
    {path: "/reset-password/:token", component: ResetPassword, name: "resetPassword"},
    {path: "/favorites", component: Favorites, name: "favorites"},
    {path: "/read", component: ReadBooks, name: "readBooks"},
    {path: "/last-viewed", component: LastViewed, name: "lastViewed"},
    {path: "/create-book", component: CreateBook, name: "createBook"},
    {
        path: "/admin",
        component: AllUsers,
        children: [
            {path: "/admin/users", component: AllUsers},
        ]
    },
    {path: "/bookshelves", component: Bookshelves, name: "bookshelves"},
    {path: "/bookshelves/create", component: CreateUpdateBookshelf, name: "createBookshelf"},
    {path: "/bookshelves/:id/edit", component: CreateUpdateBookshelf, name: "editBookshelf"},
    {path: "/book/:id", component: BookPage, beforeEnter: beforeEnter, name: "book"},
    {path: "/book/:id/edit", component: UpdateBook, beforeEnter: beforeEnter, name: "editBook"},
    {path: "/book/:id/show", component: ShowBook, beforeEnter: beforeEnter, name: "showBook"},
]

const router: Router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
