<script lang="ts">
import {defineComponent} from 'vue'
import {mapActions, mapState} from "vuex";

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
              (value: AxiosResponse | AxiosError) => {
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
  <div class="p-3 md:p-10 rounded-xl md:shadow-border">
    <div class="text-center mb-5">
      <div class="text-900 text-3xl font-medium mb-3">Добро пожаловать</div>
      <span class="text-600 font-medium line-height-3">Нет аккаунта?</span>
      <router-link to="/signup" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">Создать</router-link>
    </div>

    <div class="flex flex-col gap-4">
      <div v-if="userError.length" class="flex justify-center">
        <Message closable severity="error" @click="userError = ''">
          <span v-html="userError"></span>
        </Message>
      </div>

      <div>
        <FloatLabel variant="on">
          <InputText @keydown.enter="handleLogin" v-model="user.username" id="username-input" type="text" autofocus
                     :class="getClassesFor(user.valid.username)"/>
          <label for="username-input" class="text-900 mb-2">Логин</label>
        </FloatLabel>
      </div>

      <div>
        <FloatLabel variant="on">
          <label for="password-input" class="text-900 mb-2">Пароль</label>
          <InputText @keydown.enter="handleLogin" v-model="user.password" id="password-input" type="password"
                     :class="getClassesFor(user.valid.password)"/>
        </FloatLabel>
      </div>

      <div>
        <router-link to="/forgot-password"
                     class="font-medium no-underline ml-2 text-blue-500 text-right cursor-pointer">
          Забыли пароль?
        </router-link>
      </div>

      <Button label="Войти" icon="pi pi-user" @click="handleLogin" class="w-full"></Button>
    </div>
  </div>
</template>
