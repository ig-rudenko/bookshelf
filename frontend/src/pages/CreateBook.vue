<template>
  <Menu/>
  <div class="p-3" v-if="user?.isStaff">
    <CreateBookForm/>
  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import CreateBookForm from "@/components/CreateBookForm.vue"
import {mapState} from "vuex";
import Menu from "@/components/Menu.vue";
import LoginForm from "@/components/LoginForm.vue";

export default defineComponent({
  name: "CreateBook",
  components: {LoginForm, CreateBookForm, Menu},
  mounted() {
      if (!this.user?.isStaff) this.$router.push("/login");
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