<template>
    <a href="#main-content" class="skip-link">К содержимому</a>
    <div>
        <MegaMenu
            :model="menuItems"
            class="site-nav z-10"
            breakpoint="1160px"
            :pt="{ button: { 'aria-label': 'Открыть навигацию' } }"
        >
            <template #start>
                <a href="/" aria-label="Bookshelf — главная" class="inline-flex items-center gap-2.5 shrink-0">
                    <img src="/img/bookshelf_icon.png" alt="" class="w-8 h-8" />
                    <span class="text-xl font-semibold tracking-tight">Bookshelf</span>
                </a>
            </template>

            <template #item="{ item }">
                <a
                    :href="item.href"
                    v-if="item.root"
                    :aria-current="isCurrentItem(item) ? 'page' : undefined"
                    class="nav-link no-underline flex items-center cursor-pointer px-3 py-2"
                    :class="{ 'is-current': isCurrentItem(item) }"
                >
                    <i
                        v-if="item.icon"
                        :class="[item.icon, { 'mr-2': item.label }]"
                        :style="{ color: item.iconColor }"
                        aria-hidden="true"
                    />
                    <span :class="{ 'sr-only': !item.label }">{{
                        item.label || "Тема оформления: " + themeLabel
                    }}</span>
                    <i
                        v-if="item.items"
                        :class="[
                            'pi pi-angle-down',
                            { 'pi-angle-down ml-2': item.root, 'pi-angle-right ml-auto': !item.root },
                        ]"
                    ></i>
                </a>
                <!--Без изображения-->
                <a
                    v-else-if="item.param && !item.image && item.value"
                    class="flex items-center cursor-pointer p-2 text-900 no-underline"
                    :href="'/?' + item.param + '=' + encodeURIComponent(item.value)"
                >
                    <i v-if="item.icon" :class="item.icon"></i>
                    <span class="flex flex-col px-4">
                        <span class="text-900">{{ item.label }}</span>
                        <span v-if="item.subtext" class="white-space-nowrap">{{ item.subtext }}</span>
                    </span>
                </a>
                <!--С изображением-->
                <a
                    v-else-if="item.param && item.image"
                    class="p-1 flex flex-wrap flex-row items-center px-4 cursor-pointer text-900 no-underline"
                    :href="'/?' + item.param + '=' + (item.value || item.label)"
                >
                    <div v-if="item.image" class="p-1 px-3 rounded-md" :class="item.classes">
                        <img :src="item.image" class="h-[20px] md:h-[30px]" :alt="String(item.label)" />
                    </div>
                    <span v-if="item.subtext" class="ml-2 text-lg">{{ item.subtext }}</span>
                </a>
                <a
                    v-else-if="item.href"
                    :href="item.href"
                    class="flex items-center cursor-pointer p-2 text-900 no-underline"
                >
                    <i v-if="item.icon" :class="item.icon" :style="{ color: item.iconColor }" aria-hidden="true" />
                    <span class="flex flex-col px-3">
                        <span class="text-900">{{ item.label }}</span>
                        <span v-if="item.subtext" class="white-space-nowrap">{{ item.subtext }}</span>
                    </span>
                </a>
            </template>

            <template #end>
                <div v-if="loggedIn && user">
                    <button
                        type="button"
                        @click="toggleUserMenu"
                        class="p-2 cursor-pointer flex items-center rounded-md"
                        aria-haspopup="menu"
                        aria-controls="overlay_user_menu"
                        :aria-label="'Меню пользователя ' + user.username"
                    >
                        <Avatar
                            :label="user.username.slice(0, 2).toUpperCase()"
                            shape="circle"
                            class="!text-xs !bg-surface-200 dark:!bg-surface-800 !text-surface-700 dark:!text-surface-300"
                        />
                        <span class="hidden sm:inline-block ml-2 text-sm max-w-32 truncate">{{ user.username }}</span>
                    </button>
                    <Menu ref="userMenu" id="overlay_user_menu" :model="userItems" :popup="true" />
                </div>
            </template>
        </MegaMenu>
    </div>

    <Dialog
        v-model:visible="logoutDialogVisible"
        modal
        pt:root:class="border-0 bg-surface-200 dark:bg-surface-800 rounded-xl p-2"
        pt:mask:class="backdrop-blur-xs"
    >
        <template #container="{ closeCallback }">
            <div class="p-4 text-xl font-semibold text-surface-800 dark:text-surface-200">
                Вы уверены, что хотите выйти?
            </div>
            <div class="flex justify-end gap-2 p-2">
                <Button type="button" label="Нет" severity="secondary" autofocus @click="closeCallback"></Button>
                <Button type="button" label="Выйти" severity="danger" @click="performLogout"></Button>
            </div>
        </template>
    </Dialog>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import type { MenuItem } from "primevue/menuitem";
import { mapActions, mapState } from "vuex";
import api from "@/services/api";
import { AxiosResponse } from "axios";
import { getCurrentTheme, setAutoTheme, setDarkTheme, setLightTheme, ThemesValues } from "@/themes.ts";

export default defineComponent({
    data() {
        return {
            currentTheme: getCurrentTheme(),
            logoutDialogVisible: false,
            favoriteCount: 0,
            readCount: 0,
        };
    },

    watch: {
        loggedIn: {
            immediate: true,
            handler(value: boolean) {
                if (value) {
                    this.getFavoriteCount();
                    this.getReadCount();
                }
            },
        },
    },

    computed: {
        ...mapState({
            loggedIn: (state: any) => state.auth.status.loggedIn,
            user: (state: any) => state.auth.user,
        }),

        themeIcon() {
            if (this.currentTheme === ThemesValues.light) return "pi pi-sun";
            if (this.currentTheme === ThemesValues.dark) return "pi pi-moon";
            return "pi pi-circle";
        },
        themeLabel() {
            return { light: "светлая", dark: "тёмная", auto: "системная" }[this.currentTheme];
        },

        favoriteItem() {
            return {
                label: this.favoriteCount > 0 ? `Избранные: ${this.favoriteCount}` : "Избранное",
                icon: this.favoriteCount > 0 ? "pi pi-heart-fill" : "pi pi-heart",
                iconColor: "red",
                href: "/favorites",
                root: true,
            };
        },

        readItem() {
            return {
                label: this.readCount > 0 ? `Прочитанные: ${this.readCount}` : "Прочитанное",
                icon: "pi pi-check-square",
                iconColor: "var(--p-indigo-400)",
                href: "/read",
                root: true,
            };
        },

        menuItems() {
            let data: any[] = [
                {
                    label: "Каталог",
                    icon: "pi pi-home",
                    href: "/",
                    root: true,
                },
                {
                    label: "Категории",
                    icon: "pi pi-list",
                    root: true,
                    items: [
                        [
                            {
                                label: "Популярные издатели",
                                items: [
                                    {
                                        label: "O'Reilly",
                                        param: "publisher",
                                        classes: ["bg-white"],
                                        image: "/img/menu/publishers/oreilly.png",
                                    },
                                    {
                                        label: "Manning Publications",
                                        param: "publisher",
                                        classes: ["bg-white"],
                                        image: "/img/menu/publishers/manning.png",
                                    },
                                    {
                                        label: "Packt",
                                        param: "publisher",
                                        classes: ["bg-white"],
                                        image: "/img/menu/publishers/packt.png",
                                    },
                                    {
                                        label: "БХВ-Петербург",
                                        param: "publisher",
                                        classes: ["bg-white"],
                                        image: "/img/menu/publishers/bvh-piter.png",
                                    },
                                    {
                                        label: "No Starch Press Inc.",
                                        param: "publisher",
                                        classes: ["bg-gray-950"],
                                        image: "/img/menu/publishers/no-starch-press.png",
                                    },
                                    {
                                        label: "Питер",
                                        param: "publisher",
                                        classes: ["bg-white"],
                                        image: "/img/menu/publishers/piter.png",
                                    },
                                ],
                            },
                        ],
                        [
                            {
                                label: "Языки программирования",
                                items: [
                                    {
                                        label: "Python",
                                        param: "tags",
                                        subtext: "Python",
                                        image: "/img/menu/langs/python.svg",
                                    },
                                    { label: "Go", param: "tags", subtext: "Go", image: "/img/menu/langs/go.svg" },
                                    {
                                        label: "Java Script",
                                        param: "tags",
                                        subtext: "Java Script",
                                        image: "/img/menu/langs/js.svg",
                                    },
                                    {
                                        label: "Type Script",
                                        param: "tags",
                                        subtext: "Type Script",
                                        image: "/img/menu/langs/ts.svg",
                                    },
                                    {
                                        label: "Java",
                                        param: "tags",
                                        subtext: "Java",
                                        image: "/img/menu/langs/java.svg",
                                    },
                                    {
                                        label: "R-lang",
                                        param: "tags",
                                        subtext: "R-lang",
                                        image: "/img/menu/langs/r-lang.svg",
                                    },
                                    {
                                        label: "C%2B%2B",
                                        param: "tags",
                                        subtext: "C++",
                                        image: "/img/menu/langs/c-plusplus.svg",
                                    },
                                    {
                                        label: "Kotlin",
                                        param: "tags",
                                        subtext: "Kotlin",
                                        image: "/img/menu/langs/kotlin.svg",
                                    },
                                    { label: "PHP", param: "tags", subtext: "PHP", image: "/img/menu/langs/php.svg" },
                                ],
                            },
                        ],
                        [
                            {
                                label: "Популярные направления",
                                items: [
                                    { label: "⚙️ DevOps", param: "tags", value: "DevOps" },
                                    { label: "⚒️ Архитектура", param: "tags", value: "Архитектура" },
                                    { label: "💠 Микросервисы", param: "tags", value: "Микросервисы" },
                                    { label: "📦 Контейнеризация", param: "tags", value: "Контейнеризация" },
                                    { label: "📚 Databases", param: "tags", value: "Databases" },
                                    { label: "🤖 Machine Learning", param: "tags", value: "Machine Learning" },
                                    { label: "☁️ Cloud Native", param: "tags", value: "Cloud Native" },
                                ],
                            },
                        ],
                    ],
                },
            ];

            data.push({
                label: "Книжные полки",
                icon: "pi pi-book",
                href: "/bookshelves",
                root: true,
            });

            if (this.loggedIn) {
                data.push({
                    label: "Моя библиотека",
                    icon: "pi pi-bookmark",
                    root: true,
                    items: [
                        [
                            {
                                label: "Сохранённое и история",
                                items: [
                                    { ...this.favoriteItem, root: false },
                                    { ...this.readItem, root: false },
                                    { label: "Недавно просмотренные", icon: "pi pi-eye", href: "/last-viewed" },
                                ],
                            },
                        ],
                    ],
                });
            } else {
                data.push({
                    label: "Войти",
                    icon: "pi pi-user",
                    href: "/login",
                    root: true,
                });
            }

            if (this.user?.isSuperuser || this.user?.isStaff) {
                data.push({
                    label: "Админка",
                    icon: "pi pi-sliders-h",
                    root: true,
                    items: [
                        [
                            {
                                label: "",
                                icon: "pi pi-users",
                                classes: ["bg-white"],
                                items: [
                                    {
                                        label: "👥 Все пользователи",
                                        href: "/admin/users",
                                        classes: ["bg-white"],
                                    },
                                    {
                                        label: "📗 Добавить книгу",
                                        href: "/create-book",
                                        classes: ["bg-white"],
                                    },
                                ],
                            },
                        ],
                    ],
                });
            }

            data.push({
                label: "",
                icon: this.themeIcon,
                root: true,
                command: this.toggleTheme,
            });

            return data;
        },

        userItems() {
            if (this.loggedIn && this.user) {
                return [
                    {
                        icon: "pi pi-sign-out",
                        label: "Выйти",
                        command: () => (this.logoutDialogVisible = true),
                    },
                ];
            }
        },
    },

    methods: {
        isCurrentItem(item: MenuItem) {
            return item.href === "/"
                ? this.$route.path === "/"
                : Boolean(item.href && this.$route.path.startsWith(item.href));
        },
        ...mapActions("auth", ["logout"]),

        performLogout() {
            this.logout();
            this.logoutDialogVisible = false;
            document.location.href = "/";
        },

        toggleTheme() {
            if (this.currentTheme == "auto") setLightTheme();
            if (this.currentTheme == "light") setDarkTheme();
            if (this.currentTheme == "dark") setAutoTheme();
            this.currentTheme = getCurrentTheme();
        },

        toggleUserMenu(event: Event) {
            (<any>this.$refs.userMenu).toggle(event);
        },

        getFavoriteCount() {
            api.get("/bookmarks/favorite/count").then(
                (value: AxiosResponse<number>) => (this.favoriteCount = value.data)
            );
        },

        getReadCount() {
            api.get("/bookmarks/read/count").then((value: AxiosResponse<number>) => (this.readCount = value.data));
        },
    },
});
</script>
