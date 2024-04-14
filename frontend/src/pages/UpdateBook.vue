<template>
  <Menu/>
  <div class="p-3" v-if="user?.isStaff">
    <BookForm :editBookId="$route.params.id"/>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import BookForm from "@/components/BookForm.vue";
import LoginForm from "@/components/LoginForm.vue";
import Menu from "@/components/Menu.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "UpdateBook",
  components: {LoginForm, BookForm, Menu},
  mounted() {
    if (!this.user?.isStaff) this.$router.push("/login");
    document.title = "Редактирование книги";
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
  }
})
</script>

<style scoped>

</style>