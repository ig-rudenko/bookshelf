<script lang="ts">
import {defineComponent} from 'vue'
import {mapState, mapActions} from "vuex";

import {LoginUser} from "@/user";
import {AxiosError, AxiosResponse} from "axios";
import getVerboseAxiosError from "@/errorFmt.ts";

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
    }),
  },
  created() {
    if (this.loggedIn) {
      this.$router.push("/");
    }
  },
  methods: {
    ...mapActions("auth", ["login"]),

    getClassesFor(isValid: boolean): string[] {
      return isValid ? ['w-full', 'pb-3'] : ['w-full', 'pb-3', 'p-invalid']
    },

    handleLogin() {
      this.login(this.user)
          .then(
              (value: AxiosResponse|AxiosError) => {
                if (value.status == 200) {
                  this.$router.push("/");
                } else {
                  this.userError = (<AxiosError>value).message
                }
              },
              () => this.userError = 'Неверный логин или пароль'
          )
          .catch(
          (reason: AxiosError<any>) => {
            this.userError = getVerboseAxiosError(reason)
          }
      );
    },

    goToForgotPassword() {
      this.$router.push('/forgot-password');
    }

  },
})
</script>

<template>
  <div class="p-4 shadow-2 border-round w-full lg:w-4">
    <div class="text-center mb-5">
      <div class="text-900 text-3xl font-medium mb-3">Добро пожаловать</div>
      <span class="text-600 font-medium line-height-3">Нет аккаунта?</span>
      <a href="/signup" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Создать</a>
    </div>

    <div>
      <div v-if="userError.length" class="flex justify-content-center mb-5">
        <InlineMessage @click="userError = ''" severity="error"><span v-html="userError"></span></InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="handleLogin" v-model="user.username" id="username-input" type="text" autofocus :class="getClassesFor(user.valid.username)" />
          <label for="username-input" class="block text-900 mb-2">Username</label>
        </FloatLabel>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <label for="password-input" class="block text-900 mb-2">Password</label>
          <InputText @keydown.enter="handleLogin" v-model="user.password" id="password-input" type="password" :class="getClassesFor(user.valid.password)" />
        </FloatLabel>
      </div>

      <div class="mb-4">
        <a @click="goToForgotPassword" class="font-medium no-underline ml-2 text-blue-500 text-right cursor-pointer">Забыли пароль?</a>
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