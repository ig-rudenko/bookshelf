<template>

  <div class="flex mx-auto justify-center items-center max-w-3xl w-full">
    <div class="p-3 flex gap-2 w-full">
      <InputText fluid size="small" v-model="filters.search" placeholder="Поиск пользователей"
                 @keydown.enter="() => getUsers(1)"/>
      <Button icon="pi pi-search" @click="() => getUsers(1)"/>
    </div>
  </div>

  <div class="p-0 xl:p-2">
    <DataTable v-if="result" :value="result.results" @sort="sortUsers" scrollable class="text-xs md:text-base"
               :loading="!result" :default-sort-order="-1" sort-field="dateJoin" :sort-order="-1"
               :size="'small'" selectionMode="single"
               removableSort>
      <Column :sortable="true" field="id" header="ID">
        <template #body="slotProps">
          <span class="text-sm">ID: {{ slotProps.data.id }}</span>
        </template>
      </Column>
      <Column :sortable="true" field="username" header="Имя">
        <template #body="slotProps">
          <div class="flex items-center gap-2">
            <Avatar :image="getUserAvatar(slotProps.data.username)"/>
            <div>{{ slotProps.data.username }}</div>
          </div>
        </template>
      </Column>
      <Column :sortable="true" field="email" header="Email"></Column>
      <Column :sortable="true" field="isSuperuser" header="Superuser">
        <template #body="slotProps">
          <span v-if="slotProps.data.isSuperuser">✅</span>
        </template>
      </Column>
      <Column :sortable="true" field="isStaff" header="Сотрудник">
        <template #body="slotProps">
          <span v-if="slotProps.data.isStaff">✅</span>
        </template>
      </Column>
      <Column :sortable="true" field="dateJoin" header="Дата регистрации">
        <template #body="slotProps">
          {{ (new Date(slotProps.data.dateJoin)).toLocaleString() }}
        </template>
      </Column>
      <Column :sortable="true" field="favoritesCount" header="Избранное ❤️">
        <template #body="slotProps">
          <div class="flex flex-wrap justify-center items-center gap-1">
          <span>
            {{ slotProps.data.favoritesCount }}
          </span>
            <Badge v-if="slotProps.data.favoritesCount > 0"
                   @click="selectedUser = slotProps.data; visibleDialogFavorite = true" class="ml-2 cursor-pointer"
                   severity="success">
              Показать
            </Badge>
          </div>
        </template>
      </Column>
      <Column :sortable="true" field="readCount" header="Прочитано 📗">
        <template #body="slotProps">
          <div class="flex flex-wrap justify-center items-center gap-1">
          <span>
            {{ slotProps.data.readCount }}
          </span>
            <Badge v-if="slotProps.data.readCount > 0"
                   @click="selectedUser = slotProps.data; visibleDialogRead = true" class="ml-2 cursor-pointer"
                   severity="success">
              Показать
            </Badge>
          </div>
        </template>
      </Column>
      <Column :sortable="true" field="recentlyReadCount" header="Недавние 📖">
        <template #body="slotProps">
          {{ slotProps.data.recentlyReadCount }}
          <Badge @click="selectedUser = slotProps.data; visibleDialogLastViewed = true" class="ml-2 cursor-pointer"
                 severity="primary">
            Показать
          </Badge>
        </template>
      </Column>
    </DataTable>
  </div>

  <Paginator v-if="result"
             @page="(event: any) => getUsers(event.page+1)"
             @update:rows="(value: number) => result!.perPage = value"
             v-model="result.currentPage"
             :rows="result.perPage" :totalRecords="result.totalCount" :rowsPerPageOptions="[10, 25, 50]"/>

  <Dialog v-model:visible="visibleDialogFavorite" :style="{width: '100vw'}"
          :header="'Избранное пользователя: ' + selectedUser?.username"
          maximizable
          :modal="true">
    <Favorites v-if="selectedUser" :userID="selectedUser.id"/>
  </Dialog>

  <Dialog v-model:visible="visibleDialogRead" :style="{width: '100vw'}"
          :header="'Прочитанные книги пользователя: ' + selectedUser?.username"
          maximizable
          :modal="true">
    <ReadBooks v-if="selectedUser" :userID="selectedUser.id"/>
  </Dialog>

  <Dialog v-model:visible="visibleDialogLastViewed" :style="{width: '100vw'}"
          :header="'Недавние книги пользователя: ' + selectedUser?.username"
          maximizable
          :modal="true">
    <LastViewed v-if="selectedUser" :userID="selectedUser.id"/>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {UserDetail, UserDetailPaginatedResult, usersService} from "@/services/admin/users.ts";
import {mapState} from "vuex";
import {getUserAvatar} from "@/user.ts";
import Favorites from "@/pages/Favorites.vue";
import ReadBooks from "@/pages/ReadBooks.vue";
import LastViewed from "@/pages/LastViewed.vue";

export default defineComponent({
  name: "AllUsers",
  components: {ReadBooks, Favorites, LastViewed},
  data() {
    return {
      title: "Все пользователи",
      result: null as UserDetailPaginatedResult | null,
      visibleDialogFavorite: false,
      visibleDialogRead: false,
      visibleDialogLastViewed: false,
      selectedUser: null as UserDetail | null,
      defaultPerPage: 50,
      filters: {
        search: '',
        sortField: undefined,
        sortOrder: undefined,
      },
    }
  },
  mounted() {
    document.title = this.title;
    if (!this.loggedIn || !this.user?.isSuperuser) this.$router.push("/login");
    this.getUsers(1, "dateJoin", -1);
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
  },
  methods: {
    getUserAvatar,
    getUsers(page: number, sortField?: string, sortOrder?: number) {
      usersService.getAllUsersList(
          page,
          this.result?.perPage || this.defaultPerPage,
          sortField || this.filters.sortField,
          sortOrder || this.filters.sortOrder,
          this.filters.search,
      ).then(data => this.result = data)
    },
    sortUsers(event: any) {
      if (!this.result) return;
      this.filters.sortField = event.sortField;
      this.filters.sortOrder = event.sortOrder;
      this.getUsers(1, event.sortField, event.sortOrder)
    }
  }
})
</script>
