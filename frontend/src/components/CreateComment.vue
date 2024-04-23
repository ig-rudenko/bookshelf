<script lang="ts">
import {defineComponent} from 'vue'
import api from "@/services/api";
import {AxiosError, AxiosResponse} from "axios";
import {Comment} from "@/comment";
import getVerboseAxiosError from "@/errorFmt.ts";

export default defineComponent({
  name: "CreateComment",
  props: {
    bookId: {required: true, type: Number},
  },
  emits: ['created'],
  data() {
      return {
        text: "",
        error: "",
      }
  },
  methods: {
    sendComment() {
      if (this.text.length < 1) return;

      api.post("/comments/book/"+this.bookId, {text: this.text})
          .then(
              (res: AxiosResponse<Comment>|AxiosError) => {
                if (res.status == 201) {
                  this.$emit("created", (<AxiosResponse<Comment>>res).data);
                  this.text = "";
                  this.error = "";
                } else {
                  this.error = (<AxiosError>res).message;
                }
              }
          ).catch(
          (reason: AxiosError<any>) => {
            this.error = getVerboseAxiosError(reason)
          }
      );
    }
  }
})
</script>

<template>

  <div class="w-full" style="max-width: 45rem;">
    <Accordion>
      <AccordionTab ref="createComment" header="Создать комментарий">
        <div v-if="error" class="flex justify-content-center pb-4">
          <InlineMessage @click="error = ''" severity="error"><span v-html="error"></span></InlineMessage>
        </div>
        <div>
          <Textarea class="w-full" rows="7" v-model="text"/>
        </div>
        <Button @click="sendComment" label="Отправить"/>
      </AccordionTab>
    </Accordion>
  </div>

</template>

<style scoped>

</style>