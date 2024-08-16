<template>
  <Menu/>
  <div class="flex justify-content-center align-items-center pt-7">
    <div class="p-4 shadow-2 border-round w-full lg:w-4">
      <div v-if="resetTokenIsValid===true && resetUser && resetStatus.length == 0">

        <div class="text-center mb-5">
          <div class="text-900 text-3xl font-medium mb-3">Сброс пароля</div>
          <h4>Смена пароля для пользователя {{resetUser.username}}</h4>
        </div>

        <div v-if="error.length" class="flex justify-content-center mb-5">
          <InlineMessage @click="error = ''" severity="error"><span v-html="error"></span></InlineMessage>
        </div>
        <div class="mb-5">
          <FloatLabel>
            <InputText @keydown.enter="resetPassword" v-model="password1" id="password1-input" type="password" :class="getClassesFor(isValid)" />
            <label for="password1-input" class="block text-900 mb-2">Новый пароль</label>
          </FloatLabel>
        </div>
        <div class="mb-5">
          <FloatLabel>
            <InputText @keydown.enter="resetPassword" v-model="password2" id="password1-input" type="password" :class="getClassesFor(isValid)" />
            <label for="password1-input" class="block text-900 mb-2">Подтвердите пароль</label>
          </FloatLabel>
        </div>
        <Button label="Изменить пароль" @click="resetPassword" class="w-full"></Button>
      </div>

      <div v-if="resetTokenIsValid===false" class="flex justify-content-center">
        <InlineMessage severity="error" class="w-full">{{error}}</InlineMessage>
      </div>

      <div v-if="resetStatus.length>0">
        <InlineMessage severity="success" class="w-full mb-3">Пароль был успешно обновлен</InlineMessage>
        <Button label="Войти" @click="goToLoginPage" class="w-full"></Button>
      </div>

    </div>

  </div>
  <Footer/>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {AxiosError, AxiosResponse} from "axios";

import api from "@/services/api";
import Menu from "@/components/Menu.vue";
import Footer from "@/components/Footer.vue";
import getVerboseAxiosError from "@/errorFmt";
import {validateTwoPasswords} from "@/validators";
import {User} from "@/user.ts";
import {useRoute, useRouter} from "vue-router";

export default defineComponent({
  name: "ResetPassword",
  components: {Footer, Menu},
  data() {
    return {
      resetTokenIsValid: null as boolean|null,
      resetStatus: "",

      resetUser: null as User|null,
      resetInProcess: false,
      error: "",
      password1: "",
      password2: "",
      isValid: true,
    }
  },

  mounted() {
    document.title = "Восстановление пароля";
    api.get('/auth/reset-password/verify/'+this.token)
        .then(
            (result: AxiosResponse<User>) => {
              if (result.status == 200) {
                this.resetUser = result.data;
                this.resetTokenIsValid = true;
                this.error = ""
              }
            }
        )
        .catch(
            (error: AxiosError) => {
              this.resetTokenIsValid = false;
              this.error = getVerboseAxiosError(error)
            }
        )
  },

  computed: {
    token(): string {
      return this.route.params?.token.toString();
    },
    route() {return useRoute()},
    router() {return useRouter()},
  },

  methods: {
    passwordsIsValid(): boolean {
      this.error = validateTwoPasswords(this.password1, this.password2)
      this.isValid = this.error.length == 0;
      return this.isValid;
    },

    async resetPassword() {
      if (!this.passwordsIsValid()) return;
      const data = {
        token: this.token,
        password1: this.password1,
        password2: this.password2,
      }

      this.resetInProcess = true;
      try {
        const result = await api.post("/auth/reset-password", data)
        if (result.status == 200) {
          this.error = ""
          this.resetStatus = "Пароль был успешно обновлен"
        } else {
          this.error = result.data.detail
        }
        this.resetInProcess = true;

      } catch (error) {
        this.error = getVerboseAxiosError((<AxiosError>error))
      }
      this.resetInProcess = false;

    },

    getClassesFor(isValid: boolean): string[] {
      return isValid ? ['w-full', 'pb-3'] : ['w-full', 'pb-3', 'p-invalid']
    },

    goToLoginPage() {
      this.router.push("/login");
    }
  }
});
</script>

<style scoped>

@media (width < 600px) {
  .shadow-2 {
    box-shadow: none!important;
  }
}
</style>