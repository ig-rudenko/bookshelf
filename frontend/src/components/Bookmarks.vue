<script lang="ts">
import {defineComponent} from 'vue'
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export default defineComponent({
  name: "MarkFavorite",
  props: {
    bookId: {required: true, type: Number},
    type: {required: true, type: String},
    mark: {required: true, type: Boolean},
  },
  emits: ["updated"],
  methods: {
    toggle() {
      if (this.mark) {
        api.delete("bookmarks/" + this.bookId + "/" + this.type)
            .then((res: AxiosResponse) => {
              if (res.status == 204) {
                this.$emit("updated", false)
              }
            })
      } else {
        api.post("bookmarks/" + this.bookId + "/" + this.type)
            .then((res: AxiosResponse) => {
              if (res.status == 200) {
                this.$emit("updated", true)
              }
            })
      }
    },
  }
})
</script>

<template>
  <Button v-if="type=='favorite'"
          v-tooltip.bottom="mark?'Убрать из избранного':'Добавить в избранное'" @click="toggle" icon="pi pi-heart"
          raised :outlined="!mark" rounded/>

  <Button v-if="type=='read'"
          v-tooltip.bottom="mark?'Убрать из прочитанного':'Пометить прочитанным'" @click="toggle" icon="pi pi-book"
          raised severity="info" :outlined="!mark" rounded/>
</template>
