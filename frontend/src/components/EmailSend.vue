<template>
  <div class="p-3 md:p-10 rounded-xl md:shadow-border">
    <div class="text-center mb-5">
      <div class="text-900 text-3xl font-medium mb-3">Восстановление пароля</div>
      <router-link to="/login" class="text-blue-500 font-medium line-height-3 cursor-pointer">
        Я вспомнил пароль!
      </router-link>
    </div>

    <div>
      <div v-if="sentDetail" class="flex justify-center mb-5">
        <Message :severity="sentDetail.success?'success':'error'">{{ sentDetail.detail }}</Message>
      </div>
      <div v-if="error.length" class="flex justify-center mb-5">
        <Message @click="error = ''" severity="error"><span v-html="error"></span></Message>
      </div>

      <div class="mb-3">
        <FloatLabel variant="on">
          <InputText @keydown.enter="verifyCaptcha" v-model="email" id="email-input" type="text" autofocus
                     :class="getClassesFor(isValid)"/>
          <label for="email-input" class="block text-900 mb-2">Email</label>
        </FloatLabel>
      </div>
      <ChallengeV2 @success="sendEmail" @error="(e: Error) => error = e.toString()" ref="recaptcha"/>

      <div v-if="timeout>0" class="mb-2 text-600">
        <small>Отправить повторно можно будет через: {{ timeout }} секунд</small>
      </div>

      <Button :disabled="timeout>0" label="Отправить письмо" @click="verifyCaptcha" class="w-full"></Button>
    </div>

  </div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {ChallengeV2} from "vue-recaptcha";
import api from "@/services/api";
import {AxiosError, AxiosResponse} from "axios";
import getVerboseAxiosError from "@/errorFmt";
import {validateEmail} from "@/validators.ts";

interface SentEmailResponse {
  success: boolean
  detail: string
}

export default defineComponent({
  name: "EmailSend",
  components: {ChallengeV2,},
  data() {
    return {
      sentDetail: null as SentEmailResponse | null,
      timeout: 0,
      email: "",
      error: "",
      isValid: true,
      recaptchaToken: "",
    }
  },
  methods: {
    getClassesFor(isValid: boolean): string[] {
      return isValid ? ['w-full', 'pb-3'] : ['w-full', 'pb-3', 'p-invalid']
    },
    countTimer() {
      if (this.timeout > 0) {
        this.timeout -= 1;
        setTimeout(this.countTimer, 1000);
      }
    },
    emailIsValid(): boolean {
      return validateEmail(this.email).length == 0;
    },

    verifyCaptcha() {
      if (!this.emailIsValid()) {
        this.error = "Укажите верный email"
        return;
      }
      this.error = ""
      if (this.recaptchaToken.length == 0) {
        (<typeof ChallengeV2>this.$refs.recaptcha).execute()
      } else {
        this.sendEmail(this.recaptchaToken);
      }
    },

    sendEmail(recaptchaToken: string) {
      this.recaptchaToken = recaptchaToken
      console.log(recaptchaToken)
      const data = {
        email: this.email,
        recaptchaToken: recaptchaToken
      }

      api.post("/auth/forgot-password", data)
          .then(
              (response: AxiosResponse<SentEmailResponse>) => {
                this.sentDetail = response.data;
                if (this.sentDetail.success) {
                  this.timeout = 120;
                  setTimeout(this.countTimer, 1000);
                }
              },
          )
          .catch(
              (error: AxiosError) => {
                console.log(error)
                this.sentDetail = {success: false, detail: getVerboseAxiosError(error)}
              }
          )
    },
  }
})
</script>
