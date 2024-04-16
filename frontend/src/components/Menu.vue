<template>
  <div class="card">
    <Menubar :model="menuItems">
      <template #start>
        <a href="/">
          <Avatar class="mx-2" image="/public/bookshelf_icon.png" size="large" shape="square" />
        </a>
      </template>
      <template #item="{ item, props, hasSubmenu, root }">
        <a :href="item.href||'#'" class="flex align-items-center" v-bind="props.action">
          <Avatar :class="{ 'ml-auto': !root, 'ml-2': root }" v-if="item.avatarImage" :image="item.avatarImage" shape="circle" />
          <i v-if="item.icon" :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
          <Badge v-if="item.badge" :value="item.badge" />
          <span v-if="item.shortcut" class="ml-auto border-1 surface-border border-round surface-100 text-xs p-1">{{ item.shortcut }}</span>
          <i v-if="hasSubmenu" :class="['pi pi-angle-down', { 'pi-angle-down ml-2': root, 'pi-angle-right ml-auto': !root }]"></i>
        </a>
      </template>
    </Menubar>
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


export default defineComponent({
  data() {
    return {
      themeIcon: themeSwitch.current.includes("light")?"pi pi-moon":"pi pi-sun",
      logoutDialogVisible: false,
    };
  },

  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),

    menuItems() {
      let data: any[] = [
        {
          label: "Главная",
          icon: "pi pi-book",
          href: "/",
        }
      ]

      if (this.loggedIn) {
        if (this.user?.isStaff) {
          data.push(
              {
                label: "Добавить книгу",
                icon: "pi pi-plus pi-book",
                href: "/create-book",
              }
          )
        }
        data.push(
            {
              label: this.user?.username,
              avatarImage: "https://primefaces.org/cdn/primevue/images/avatar/amyelsner.png",
              items: [
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
        )
      } else {
        data.push(
            {
              label: "Войти",
              icon: "pi pi-user",
              href: "/login",
            }
        )
      }
      data.push(
          {
            label: "",
            icon: this.themeIcon,
            command: this.toggleTheme
          }
      )

      return data
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

  }

});
</script>
