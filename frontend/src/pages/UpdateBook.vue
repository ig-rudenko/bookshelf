<template>
  <div class="p-3" v-if="user">
    <BookForm :editBookId="Number($route.params.id)"/>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import BookForm from "@/components/BookForm.vue";
import LoginForm from "@/components/LoginForm.vue";
import {mapState} from "vuex";

export default defineComponent({
  name: "UpdateBook",
  components: {LoginForm, BookForm},
  mounted() {
    if (!this.user) this.$router.push("/login");
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
