<script lang="ts">
import {defineComponent} from 'vue'
import {mapState} from "vuex";

import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Toast from 'primevue/toast';

import {LoginUser} from "@/user";

export default defineComponent({
  name: "LoginForm",

  components: {
    Button,
    InputText,
    Password,
    Toast,
  },

  data() {
    return {
      user: new LoginUser(),
    };
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      state: (state: any) => state,
    }),
  },
  created() {
    if (this.loggedIn) {
      this.$router.push("/");
    }
  },
  methods: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn
    }),
    handleLogin() {
      if (!this.user.isValid) return;

      this.state.dispatch("auth/login", this.user).then(
          () => this.$router.push("/"),
          () => this.$toast.add({ severity: 'error', summary: 'Error', detail: 'Неверный логин или пароль', life: 3000 })
      );
    },

  },
})
</script>

<template>
  <div class="surface-card p-4 shadow-2 border-round w-full lg:w-6">
    <div class="text-center mb-5">
      <img src="#" alt="Image" height="50" class="mb-3" />
      <div class="text-900 text-3xl font-medium mb-3">Welcome Back</div>
      <span class="text-600 font-medium line-height-3">Don't have an account?</span>
      <a class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Create today!</a>
    </div>

    <div>
      <label for="email1" class="block text-900 font-medium mb-2">Email</label>
      <InputText id="email1" type="text" placeholder="Email address" class="w-full mb-3" />

      <label for="password1" class="block text-900 font-medium mb-2">Password</label>
      <InputText id="password1" type="password" placeholder="Password" class="w-full mb-3" />

      <div class="flex align-items-center justify-content-between mb-6">
        <div class="flex align-items-center">
          <Checkbox id="rememberme1" :binary="true" class="mr-2"></Checkbox>
          <label for="rememberme1">Remember me</label>
        </div>
        <a class="font-medium no-underline ml-2 text-blue-500 text-right cursor-pointer">Forgot password?</a>
      </div>

      <Button label="Sign In" icon="pi pi-user" @click="handleLogin" class="w-full"></Button>
    </div>
  </div>
</template>

<style scoped>

</style>