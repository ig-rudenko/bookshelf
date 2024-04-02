<script lang="ts">
import {defineComponent} from 'vue'
import {mapState, mapActions} from "vuex";

import {RegisterUser} from "@/user";
import {AxiosError, AxiosResponse} from "axios";
import getVerboseAxiosError from "@/errorFmt.ts";

export default defineComponent({
  name: "LoginForm",

  data() {
    return {
      user: new RegisterUser(),
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
    ...mapActions("auth", ["register"]),

    getClassesFor(isValid: boolean): string[] {
      return isValid ? ['w-full', 'pb-3'] : ['w-full', 'pb-3', 'p-invalid']
    },

    handleRegister() {
      if (!this.user.isValid) return;

      this.register(this.user)
          .then(
          (value: AxiosResponse|AxiosError) => {
            if (value.status == 200) this.$router.push("/");
            this.userError = (<AxiosError>value).message
          },
      ).catch(
          (reason: AxiosError<any>) => {
            this.userError = getVerboseAxiosError(reason)
          }
      );
    },

  },
})
</script>

<template>
  <div class="p-4 shadow-2 border-round w-full lg:w-4">
    <div class="text-center mb-5">
<!--      <img src="#" alt="Image" height="50" class="mb-3" />-->
      <div class="text-900 text-3xl font-medium mb-3">Регистрация</div>
      <a href="/login" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">У меня уже есть аккаунт</a>
    </div>

    <div>
      <div v-if="userError.length" class="flex justify-content-center pb-4">
        <InlineMessage @click="userError = ''" severity="error"><span v-html="userError"></span></InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="handleRegister" v-model="user.username" id="username-input" type="text" :class="getClassesFor(user.valid.username)" />
          <label for="username-input" class="block text-900 mb-2">Username</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.username" severity="error">{{user.valid.usernameError}}</InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="handleRegister" v-model="user.email" id="email-input" type="text" :class="getClassesFor(user.valid.email)" />
          <label for="email-input" class="block text-900 mb-2">Email</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.email" severity="error">{{user.valid.emailError}}</InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <Password @keydown.enter="handleRegister" v-model="user.password" id="password-input" :input-class="getClassesFor(user.valid.password)" class="w-full" />
          <label for="password-input" class="block text-900 mb-2">Password</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.password" severity="error">{{user.valid.passwordError}}</InlineMessage>
      </div>

      <FloatLabel class="mb-5">
        <InputText @keydown.enter="handleRegister" v-model="user.password2" id="password-input" type="password" :class="getClassesFor(user.valid.password)" />
        <label for="password-input" class="block text-900 mb-2">Confirm password</label>
      </FloatLabel>

      <Button label="Sign In" icon="pi pi-user" @click="handleRegister" class="w-full"></Button>
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