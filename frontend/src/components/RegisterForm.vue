<script lang="ts">
import {defineComponent} from 'vue'
import {mapActions, mapState} from "vuex";
import {ChallengeV2} from "vue-recaptcha";

import {RegisterUser} from "@/user";
import {AxiosError} from "axios";
import getVerboseAxiosError from "@/errorFmt.ts";

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
  },
  created() {
    if (this.loggedIn) {
      this.$router.push("/");
    }
  },
  methods: {
    ...mapActions("auth", ["register"]),
    verifyCaptcha() {
      if (!this.user.isValid) return;
      (<typeof ChallengeV2>this.$refs.recaptcha).execute()
    },
    handleRegister(recaptchaToken: string) {
      this.user.recaptchaToken = recaptchaToken;

      this.register(this.user)
          .then(() => this.$router.push("/login"))
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
  <div class="p-3 md:p-10 rounded-xl md:shadow-border">
    <div class="text-center mb-5">
      <div class="text-3xl font-medium mb-3">Регистрация</div>
      <router-link to="/login" class="font-medium no-underline ml-2 text-blue-500 cursor-pointer">
        У меня уже есть аккаунт
      </router-link>
    </div>

    <div class="flex flex-col gap-4">
      <div v-if="userError" class="flex justify-center pb-4">
        <Message @click="userError = ''" severity="error"><span v-html="userError"></span></Message>
      </div>

      <div>
        <FloatLabel variant="on">
          <InputText @keydown.enter="verifyCaptcha" v-model="user.username" id="username-input" type="text" autofocus
                     class="w-full"
                     :class="{'p-invalid': !user.valid.username}"/>
          <label for="username-input">Логин</label>
        </FloatLabel>
        <Message v-if="!user.valid.username" severity="error">{{ user.valid.usernameError }}</Message>
      </div>

      <div>
        <FloatLabel variant="on">
          <InputText @keydown.enter="verifyCaptcha" v-model="user.email" id="email-input" type="text"
                     class="w-full"
                     :class="{'p-invalid': !user.valid.email}"/>
          <label for="email-input">Email</label>
        </FloatLabel>
        <Message v-if="!user.valid.email" severity="error">{{ user.valid.emailError }}</Message>
      </div>

      <div>
        <FloatLabel variant="on">
          <Password @keydown.enter="verifyCaptcha" v-model="user.password" id="password1-input"
                    class="w-full"
                    input-class="w-full"
                    promptLabel="Введите пароль"
                    weakLabel="Слишком легкий" mediumLabel="Средний" strongLabel="Сильный пароль"
                    :class="{'p-invalid': !user.valid.password}"/>
          <label for="password1-input">Пароль</label>
        </FloatLabel>
        <Message v-if="!user.valid.password" severity="error">{{ user.valid.passwordError }}</Message>
      </div>

      <FloatLabel variant="on">
        <InputText @keydown.enter="verifyCaptcha" v-model="user.password2" id="password2-input" type="password"
                   class="w-full"
                   :class="{'p-invalid': !user.valid.password}"/>
        <label for="password2-input">Повторите пароль</label>
      </FloatLabel>

      <ChallengeV2 v-model="user.recaptchaToken" @success="handleRegister" class="absolute"
                   @error="(e: Error) => userError = e.toString()" ref="recaptcha"/>
      <Button label="Зарегистрироваться" icon="pi pi-user" @click="verifyCaptcha" class="w-full"></Button>
    </div>
  </div>
</template>
