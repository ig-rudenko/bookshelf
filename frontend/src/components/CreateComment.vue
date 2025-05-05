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

      api.post("/comments/book/" + this.bookId, {text: this.text})
          .then(
              (res: AxiosResponse<Comment> | AxiosError) => {
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

  <div class="w-full max-w-[45rem]">
    <Accordion value="1">
      <AccordionPanel value="0">
        <AccordionHeader>Создать комментарий</AccordionHeader>
        <AccordionContent>
          <div class="pt-3">
            <div v-if="error" class="flex justify-center pb-4">
              <Message @click="error = ''" severity="error"><span v-html="error"></span></Message>
            </div>
            <div>
              <Textarea class="w-full" auto-resize rows="3" v-model="text"/>
            </div>
            <Button @click="sendComment" label="Отправить"/>
          </div>
        </AccordionContent>
      </AccordionPanel>
    </Accordion>
  </div>

</template>
