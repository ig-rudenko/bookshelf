<template>
  <div>
    <MegaMenu :model="menuItems" class="dark:bg-gray-900 z-10" scrollHeight="100vh">
      <template #start>
        <a href="/">
          <Avatar class="mx-2" image="/img/bookshelf_icon.png" size="large" shape="square"/>
        </a>
      </template>

      <template #item="{ item }">
        <a :href="item.href" v-if="item.root"
           class="text-900 no-underline flex items-center cursor-pointer px-3 py-2">
          <i :style="{color: item.iconColor}" :class="item.icon"/>
          <span class="ml-2">{{ item.label }}</span>
          <i v-if="item.items"
             :class="['pi pi-angle-down', { 'pi-angle-down ml-2': item.root, 'pi-angle-right ml-auto': !item.root }]"></i>
        </a>
        <a v-else-if="item.param && !item.image" :href="'/?'+item.param+'='+item.label"
           class="flex items-center cursor-pointer p-2 text-900 no-underline">
          <i v-if="item.icon" :class="item.icon"></i>
          <span class="flex flex-col px-4">
            <span class="text-900">{{ item.label }}</span>
            <span v-if="item.subtext" class="white-space-nowrap">{{ item.subtext }}</span>
          </span>
        </a>
        <a v-else-if="item.param && item.image"
           class="p-1 flex flex-wrap flex-row items-center px-4 cursor-pointer text-900 no-underline"
           :href="'/?'+item.param+'='+item.label">
          <div class="p-1 px-3 rounded-md" :class="item.classes">
            <img :src="item.image" class="h-[20px] md:h-[30px]" :alt="String(item.label)"/>
          </div>
          <span v-if="item.subtext" class="ml-2 text-lg">{{ item.subtext }}</span>
        </a>
        <a v-else-if="item.href" :href="item.href" class="flex items-center cursor-pointer p-2 text-900 no-underline">
          <span class="flex flex-col px-4">
            <span class="text-900">{{ item.label }}</span>
            <span v-if="item.subtext" class="white-space-nowrap">{{ item.subtext }}</span>
          </span>
        </a>
      </template>

      <template #end>
        <div v-if="loggedIn && user" @click="toggleUserMenu" class="p-2 cursor-pointer flex items-center">
          <Avatar :image="getUserAvatar(user.username)"/>
          <span class="ml-2">{{ user.username }}</span>
          <Menu ref="userMenu" id="overlay_user_menu" :model="userItems" :popup="true"/>
        </div>
      </template>

    </MegaMenu>
  </div>

  <Dialog v-model:visible="logoutDialogVisible" modal
          pt:root:class="border-0 bg-surface-200 dark:bg-surface-800 rounded-xl p-2"
          pt:mask:class="backdrop-blur-xs">
    <template #container="{ closeCallback }">
      <div class="p-4 text-xl font-semibold text-surface-800 dark:text-surface-200">Вы уверены, что хотите выйти?</div>
      <div class="flex justify-end gap-2 p-2">
        <Button type="button" label="Нет" severity="secondary" autofocus @click="closeCallback"></Button>
        <Button type="button" label="Выйти" severity="danger" @click="performLogout"></Button>
      </div>
    </template>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from "vue";
import {mapActions, mapState} from "vuex";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import {getCurrentTheme, setAutoTheme, setDarkTheme, setLightTheme, ThemesValues} from "@/themes.ts";
import {getUserAvatar} from "@/user.ts";


export default defineComponent({
  data() {
    return {
      currentTheme: getCurrentTheme(),
      logoutDialogVisible: false,
      favoriteCount: 0,
      readCount: 0,
    };
  },

  mounted() {
    if (this.loggedIn) {
      this.getFavoriteCount();
      this.getReadCount();
    }
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

    favoriteItem() {
      return {
        label: this.favoriteCount > 0 ? `Избранные: ${this.favoriteCount}` : "Избранное",
        icon: this.favoriteCount > 0 ? "pi pi-heart-fill" : "pi pi-heart",
        iconColor: "red",
        href: "/favorites",
        root: true,
      }
    },

    readItem() {
      return {
        label: this.readCount > 0 ? `Прочитанные: ${this.readCount}` : "Прочитанное",
        icon: "pi pi-check-square",
        iconColor: "var(--p-indigo-400)",
        href: "/read",
        root: true,
      }
    },

    menuItems() {
      let data: any[] = [
        {
          label: "Главная",
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
                    classes: ['bg-white'],
                    image: "/img/menu/publishers/oreilly.png"
                  },
                  {
                    label: 'Manning Publications',
                    param: "publisher",
                    classes: ['bg-white'],
                    image: "/img/menu/publishers/manning.png"
                  },
                  {label: 'Packt', param: "publisher", classes: ['bg-white'], image: "/img/menu/publishers/packt.png"},
                  {
                    label: 'БХВ-Петербург',
                    param: "publisher",
                    classes: ['bg-white'],
                    image: "/img/menu/publishers/bvh-piter.png"
                  },
                  {
                    label: 'No Starch Press Inc.',
                    param: "publisher",
                    classes: ['bg-gray-950'],
                    image: "/img/menu/publishers/no-starch-press.png"
                  },
                  {label: 'Питер', param: "publisher", classes: ['bg-white'], image: "/img/menu/publishers/piter.png"},
                ]
              }
            ],
            [
              {
                label: "Языки программирования",
                items: [
                  {label: 'Python', param: "tags", subtext: "Python", image: "/img/menu/langs/python.svg"},
                  {label: 'Go', param: "tags", subtext: "Go", image: '/img/menu/langs/go.svg'},
                  {label: 'Java Script', param: "tags", subtext: "Java Script", image: "/img/menu/langs/js.svg"},
                  {label: 'Type Script', param: "tags", subtext: "Type Script", image: "/img/menu/langs/ts.svg"},
                  {label: 'Java', param: "tags", subtext: "Java", image: "/img/menu/langs/java.svg"},
                  {label: 'R-lang', param: "tags", subtext: "R-lang", image: "/img/menu/langs/r-lang.svg"},
                  {label: 'C%2B%2B', param: "tags", subtext: "C++", image: "/img/menu/langs/c-plusplus.svg"},
                  {label: 'Kotlin', param: "tags", subtext: "Kotlin", image: "/img/menu/langs/kotlin.svg"},
                  {label: 'PHP', param: "tags", subtext: "PHP", image: "/img/menu/langs/php.svg"},
                ]
              }
            ],
            [
              {
                label: "Популярные направления",
                items: [
                  {label: "⚙️ DevOps", param: "tags"},
                  {label: "⚒️ Архитектура", param: "tags"},
                  {label: "💠 Микросервисы", param: "tags"},
                  {label: "📦 Контейнеризация", param: "tags"},
                  {label: "📚 Databases", param: "tags"},
                  {label: "🤖 Machine Learning", param: "tags"},
                  {label: "☁️ Cloud Native", param: "tags"},
                ]
              }
            ],
          ]
        }
      ]

      data.push({
        label: "Книжные полки",
        icon: "pi pi-book",
        href: "/bookshelves",
        root: true,
      })

      if (this.loggedIn) {

        data.push(this.favoriteItem)
        data.push(this.readItem)
        data.push(
            {
              label: "Недавние",
              icon: "pi pi-eye",
              // iconColor: "red",
              href: "/last-viewed",
              root: true,
            }
        )

        if (this.user?.isStaff) {
          data.push({label: "Добавить книгу", icon: "pi pi-plus", href: "/create-book", root: true})
        }

      } else {
        data.push(
            {
              label: "Войти",
              icon: "pi pi-user",
              href: "/login",
              root: true,
            }
        )
      }

      if (this.user?.isSuperuser) {
        data.push(
            {
              label: "Админка",
              icon: "pi pi-sliders-h",
              root: true,
              items: [
                [
                  {
                    label: "",
                    icon: "pi pi-users",
                    classes: ['bg-white'],
                    items: [
                      {
                        label: "Все пользователи",
                        href: "/admin/users",
                        classes: ['bg-white'],
                      },
                    ]
                  }
                ]
              ]
            }
        );
      }

      data.push(
          {
            label: "",
            icon: this.themeIcon,
            root: true,
            command: this.toggleTheme
          }
      )

      return data
    },

    userItems() {
      if (this.loggedIn && this.user) {
        return [
          {
            icon: "pi pi-sign-out",
            label: "Выйти",
            command: () => this.logoutDialogVisible = true
          }
        ]
      }
    }

  },

  methods: {
    getUserAvatar,
    ...mapActions("auth", ["logout"]),

    performLogout() {
      this.logout()
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
      (<any>this.$refs.userMenu).toggle(event)
    },

    getFavoriteCount() {
      api.get("/bookmarks/favorite/count").then((value: AxiosResponse<number>) => this.favoriteCount = value.data)
    },

    getReadCount() {
      api.get("/bookmarks/read/count").then((value: AxiosResponse<number>) => this.readCount = value.data)
    }

  }

});
</script>
