<script lang="ts">
import {defineComponent} from 'vue'
import {mapState, mapActions} from "vuex";

import {LoginUser} from "@/user";
import {AxiosError, AxiosResponse} from "axios";

export default defineComponent({
  name: "LoginForm",

  data() {
    return {
      user: new LoginUser(),
      userError: "",
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
    ...mapActions("auth", ["login"]),
    handleLogin() {
      if (!this.user.isValid) return;

      this.login(this.user)
          .then(
          (value: AxiosResponse|AxiosError) => {
            if (value.status == 200) this.$router.push("/");
            this.userError = (<AxiosError>value).message
          },
          () => this.userError = 'Неверный логин или пароль'
      ).catch(
          (reason: AxiosError) => this.userError = reason.message
      );
    },

  },
})
</script>

<template>
  <div class="surface-card p-4 shadow-2 border-round w-full lg:w-4">
    <div class="text-center mb-5">
      <img src="#" alt="Image" height="50" class="mb-3" />
      <div class="text-900 text-3xl font-medium mb-3">Welcome Back</div>
      <span class="text-600 font-medium line-height-3">Don't have an account?</span>
      <a class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Create today!</a>
    </div>

    <div>
      <div v-if="userError.length" class="flex justify-content-center pb-4">
        <InlineMessage @click="userError = ''" severity="error">{{userError}}</InlineMessage>
      </div>

      <label for="username-input" class="block text-900 font-medium mb-2">
        Username <span v-if="!user.valid.username">{{}}</span>
      </label>

      <InputText v-model="user.username" id="username-input" type="text" :class="user.valid.username?['w-full', 'mb-3']:['w-full', 'mb-3', 'p-invalid']" />

      <label for="password-input" class="block text-900 font-medium mb-2">Password</label>
      <InputText v-model="user.password" id="password-input" type="password" :class="user.valid.password?['w-full', 'mb-3']:['w-full', 'mb-3', 'p-invalid']" />

      <div class="mb-4">
        <a class="font-medium no-underline ml-2 text-blue-500 text-right cursor-pointer">Forgot password?</a>
      </div>

      <Button label="Sign In" icon="pi pi-user" @click="handleLogin" class="w-full"></Button>
    </div>
  </div>
</template>

<style scoped>

@media (width < 600px) {
  .shadow-2 {
    box-shadow: none!important;
  }
}
</style>