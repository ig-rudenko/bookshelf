<template>
  <Menu/>
  <div class="p-3" v-if="user?.isStaff">
    <BookForm/>
  </div>
  <Footer/>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import BookForm from "@/components/BookForm.vue"
import {mapState} from "vuex";
import Menu from "@/components/Menu.vue";
import LoginForm from "@/components/LoginForm.vue";
import Footer from "@/components/Footer.vue";
import {useRouter} from "vue-router";

export default defineComponent({
  name: "CreateBook",
  components: {Footer, LoginForm, BookForm, Menu},
  mounted() {
      if (!this.user?.isStaff) this.router.push("/login");
      document.title = "Добавление книги";
  },
  computed: {
      ...mapState({
        loggedIn: (state: any) => state.auth.status.loggedIn,
        user: (state: any) => state.auth.user,
      }),
      router() {return useRouter()},
    }
})
</script>

<style scoped>

</style>