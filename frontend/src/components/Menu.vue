<template>
  <div class="card">
    <MegaMenu :model="menuItems">
      <template #start>
        <a href="/">
          <Avatar class="mx-2" image="/img/bookshelf_icon.png" size="large" shape="square" />
        </a>
      </template>

      <template #item="{ item }">
        <a :href="item.href" v-if="item.root" class="text-900 no-underline flex align-items-center cursor-pointer px-3 py-2">
          <i :style="{color: item.iconColor}" :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
          <i v-if="item.items" :class="['pi pi-angle-down', { 'pi-angle-down ml-2': item.root, 'pi-angle-right ml-auto': !item.root }]"></i>
        </a>
        <a v-else-if="!item.image" :href="'/?'+item.param+'='+item.label" class="flex align-items-center cursor-pointer p-2 text-900 no-underline">
          <i v-if="item.icon" :class="item.icon"></i>
          <span class="inline-flex flex-column px-4">
            <span class="text-900">{{ item.label }}</span>
            <span v-if="item.subtext" class="white-space-nowrap">{{ item.subtext }}</span>
          </span>
        </a>
        <a v-else class="p-1 flex flex-wrap align-items-center px-4 cursor-pointer text-900 no-underline" :href="'/?'+item.param+'='+item.label">
          <div class="p-1 px-3 border-round-md" :class="item.classes">
            <img :src="item.image" height="20" :alt="String(item.label)"/>
          </div>
          <span v-if="item.subtext" class="ml-2 text-lg">{{ item.subtext }}</span>
        </a>
      </template>

      <template #end>
        <div v-if="loggedIn && user" @click="toggleUserMenu" class="p-2 cursor-pointer flex align-items-center">
          <Avatar :image="userAvatarImage" />
          <span class="ml-2">{{user.username}}</span>
          <Menu ref="userMenu" id="overlay_user_menu" :model="userItems" :popup="true" />
        </div>
      </template>

    </MegaMenu>
  </div>

  <Dialog v-model:visible="logoutDialogVisible" class="pt-2" :show-header="false" modal :style="{ width: '25rem' }">
      <div class="flex align-items-center py-4">
        <i class="text-5xl pi pi-exclamation-circle mr-2" />
        <h3>Вы уверены, что хотите выйти?</h3>
      </div>

    <div class="flex justify-content-end gap-2">
      <Button type="button" severity="secondary" label="Остаться" @click="logoutDialogVisible = false"></Button>
      <Button type="button" severity="danger" label="Выйти" @click="performLogout"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from "vue";
import themeSwitch from "@/theming";
import {mapActions, mapState} from "vuex";
import Menu from "primevue/menu";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";


export default defineComponent({
  data() {
    return {
      themeIcon: themeSwitch.current.includes("light")?"pi pi-moon":"pi pi-sun",
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

    favoriteItem() {
      return {
        label: this.favoriteCount>0?`Избранные: ${this.favoriteCount}`:"Избранное",
        icon: this.favoriteCount>0?"pi pi-heart-fill":"pi pi-heart",
        iconColor: "red",
        href: "/favorites",
        root: true,
      }
    },

    readItem() {
      return {
        label: this.readCount>0?`Прочитанные: ${this.readCount}`:"Прочитанное",
        icon: "pi pi-check-square",
        iconColor: "var(--primary-400)",
        href: "/read",
        root: true,
      }
    },

    menuItems() {
      let data: any[] = [
        {
          label: "Главная",
          icon: "pi pi-book",
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
                  { label: "O'Reilly", param: "publisher", classes: ['bg-white'], image: "https://cdn.oreillystatic.com/images/sitewide-headers/oreilly_logo_mark_red.svg"},
                  { label: 'Manning Publications', param: "publisher", classes: ['bg-white'], image: "https://www.manning.com/assets/manningLettersBlack-0ebe3f78d807742e74e80ce85f130096.svg"},
                  { label: 'Packt', param: "publisher", classes: ['bg-white'], image: "https://www.packtpub.com/images/logo-new.svg"},
                  { label: 'БХВ-Петербург', param: "publisher", classes: ['bg-white'], image: "https://textarchive.ru/images/716/1430749/6b3cdbad.gif"},
                  { label: 'No Starch Press Inc.', param: "publisher", classes: ['bg-black-alpha-90'], image: "https://nostarch.com/sites/all/themes/nostarch/logo.png"},
                  { label: 'Питер', param: "publisher", classes: ['bg-white'], image: "https://segment.ru/upload/usersImg/ab0/Piter.jpg"},
                ]
              }
            ],
            [
              {
                label: "Языки программирования",
                items: [
                  { label: 'Python', param: "tags", subtext: "Python", image: "https://www.vectorlogo.zone/logos/python/python-icon.svg" },
                  { label: 'Go', param: "tags", subtext: "Go", image: 'https://www.vectorlogo.zone/logos/golang/golang-official.svg' },
                  { label: 'Java Script', param: "tags", subtext: "Java Script", image: "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/javascript/javascript-original.svg" },
                  { label: 'Java', param: "tags", subtext: "Java", image: "https://www.vectorlogo.zone/logos/java/java-icon.svg" },
                  { label: 'R-lang', param: "tags", subtext: "R-lang", image: "https://www.vectorlogo.zone/logos/r-project/r-project-official.svg" },
                  { label: 'C%2B%2B', param: "tags", subtext: "C++", image: "https://www.vectorlogo.zone/logos/isocpp/isocpp-icon.svg" },
                  { label: 'Kotlin', param: "tags", subtext: "Kotlin", image: "https://www.vectorlogo.zone/logos/kotlinlang/kotlinlang-icon.svg" },
                ]
              }
            ],
            [
              {
                label: "Популярные направления",
                items: [
                  { label: "DevOps", param: "tags"},
                  { label: "Архитектура", param: "tags"},
                  { label: "Микросервисы", param: "tags"},
                  { label: "Контейнеризация", param: "tags"},
                  { label: "Databases", param: "tags"},
                  { label: "Machine Learning", param: "tags"},
                  { label: "Cloud Native", param: "tags"},
                ]
              }
            ],
          ]
        }
      ]

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
          data.push({ label: "Добавить книгу", icon: "pi pi-plus", href: "/create-book", root: true })
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

    userAvatarImage() {
      if (this.user?.username) {
        return 'https://ui-avatars.com/api/?size=32&name='+this.user.username+'&font-size=0.33&background=random&rounded=true'
      }
      return ""
    },

    userItems () {
      if (this.loggedIn && this.user) {
        return [
          {
            label: "Профиль",
            icon: "pi pi-user",
          },
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
    ...mapActions("auth", ["logout"]),

    performLogout() {
      this.logout()
      this.logoutDialogVisible = false;
      document.location.href = "/";
    },

    toggleTheme() {
      this.$primevue.changeTheme(themeSwitch.current, themeSwitch.other, "theme-link", () => {})
      themeSwitch.toggle()
      this.themeIcon = themeSwitch.current.includes("light")?"pi pi-moon":"pi pi-sun"
    },

    toggleUserMenu(event: Event) {
      (<Menu>this.$refs.userMenu).toggle(event)
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
