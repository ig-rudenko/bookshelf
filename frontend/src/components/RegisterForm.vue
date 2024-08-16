<script lang="ts">
import {defineComponent} from 'vue'
import {mapActions, mapState} from "vuex";
import {ChallengeV2} from "vue-recaptcha";

import {RegisterUser} from "@/user";
import {AxiosError} from "axios";
import getVerboseAxiosError from "@/errorFmt.ts";
import {useRouter} from "vue-router";

export default defineComponent({
  name: "LoginForm",
  components: {ChallengeV2,},
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
    router() {return useRouter()},
  },
  created() {
    if (this.loggedIn) {
      this.router.push("/");
    }
  },
  methods: {
    ...mapActions("auth", ["register"]),

    getClassesFor(isValid: boolean): string[] {
      return isValid ? ['w-full', 'pb-3'] : ['w-full', 'pb-3', 'p-invalid']
    },
    verifyCaptcha() {
      if (!this.user.isValid) return;
      (<typeof ChallengeV2>this.$refs.recaptcha).execute()
    },
    handleRegister(recaptchaToken: string) {
      this.user.recaptchaToken = recaptchaToken;

      this.register(this.user)
          .then(() => this.router.push("/login"))
          .catch(
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
      <div class="text-900 text-3xl font-medium mb-3">Регистрация</div>
      <a href="/login" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">У меня уже есть аккаунт</a>
    </div>

    <div>
      <div v-if="userError" class="flex justify-content-center pb-4">
        <InlineMessage @click="userError = ''" severity="error"><span v-html="userError"></span></InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="verifyCaptcha" v-model="user.username" id="username-input" type="text" autofocus :class="getClassesFor(user.valid.username)" />
          <label for="username-input" class="block text-900 mb-2">Username</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.username" severity="error">{{user.valid.usernameError}}</InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="verifyCaptcha" v-model="user.email" id="email-input" type="text" :class="getClassesFor(user.valid.email)" />
          <label for="email-input" class="block text-900 mb-2">Email</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.email" severity="error">{{user.valid.emailError}}</InlineMessage>
      </div>

      <div class="mb-5">
        <FloatLabel>
          <InputText @keydown.enter="verifyCaptcha" v-model="user.password" id="password1-input" type="password" :class="getClassesFor(user.valid.password)" />
          <label for="password1-input" class="block text-900 mb-2">Password</label>
        </FloatLabel>
        <InlineMessage v-if="!user.valid.password" severity="error">{{user.valid.passwordError}}</InlineMessage>
      </div>

      <FloatLabel class="mb-5">
        <InputText @keydown.enter="verifyCaptcha" v-model="user.password2" id="password2-input" type="password" :class="getClassesFor(user.valid.password)" />
        <label for="password2-input" class="block text-900 mb-2">Confirm password</label>
      </FloatLabel>

      <ChallengeV2 v-model="user.recaptchaToken" @success="handleRegister" @error="(e: Error) => userError = e.toString()" ref="recaptcha" />
      <Button label="Sign In" icon="pi pi-user" @click="verifyCaptcha" class="w-full"></Button>
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