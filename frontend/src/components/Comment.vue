<template>
  <Card class="border-1 max-w-[45rem] w-full border-gray-400 dark:border-gray-600">
    <template #subtitle>
      <div class="flex flex-row items-center justify-between">
        <div class="flex flex-row items-center gap-2">
          <Avatar size="normal"
                  :image="'https://ui-avatars.com/api/?size=32&name='+comment.user.username+'&font-size=0.33&background=random&rounded=true'"/>
          <span class="mx-2">{{ comment.user.username }}</span>
          <div class="text-sm flex items-center gap-2">
            <i class="pi pi-calendar"/>
            <div>{{ verboseDate(comment.createdAt) }}</div>
          </div>
        </div>
        <div v-if="comment.user.id == user?.id">
          <Button @click="editMode = !editMode" rounded text icon="pi pi-pencil" size="small" severity="warn"/>
          <Button @click="deleteDialogVisible = true" rounded text icon="pi pi-trash" size="small" severity="danger"/>
        </div>
      </div>
    </template>
    <template #content>
      <div v-if="editMode">
        <Textarea class="w-full" rows="7" v-model="commentText"/>
        <Button severity="success" label="Обновить" @click="updateComment"/>
      </div>
      <div v-else v-html="textToHtml(wrapLinks(comment.text))"></div>
    </template>
  </Card>

  <Dialog v-model:visible="deleteDialogVisible" class="pt-2" :show-header="false" modal :style="{ width: '25rem' }">
    <div class="text-xl flex items-center gap-4 py-5">
      <i class="pi pi-exclamation-circle text-red-500 !text-3xl"/>
      Вы уверены, что хотите удалить комментарий?
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" severity="success" icon="pi pi-times" label="Не удалять" autofocus
              @click="deleteDialogVisible = false"></Button>
      <Button type="button" severity="danger" icon="pi pi-trash" label="Удалить" @click="deleteComment"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {Comment} from "@/comment";
import {textToHtml, verboseDate, wrapLinks} from "../formatter";
import {mapState} from "vuex";
import api from "@/services/api";
import {AxiosError, AxiosResponse} from "axios";
import getVerboseAxiosError from "@/errorFmt";

export default defineComponent({
  name: "Comment",
  props: {
    comment: {required: true, type: Comment},
  },
  emits: ['comment:delete', 'comment:update'],
  data() {
    return {
      deleteDialogVisible: false,
      error: "",
      commentText: this.comment.text,
      editMode: false,
    }
  },
  computed: {
    ...mapState({
      loggedIn: (state: any) => state.auth.status.loggedIn,
      user: (state: any) => state.auth.user,
    }),
  },
  methods: {
    wrapLinks,
    textToHtml,
    verboseDate,
    deleteComment() {
      api.delete("/comments/" + this.comment.id)
          .then((response: AxiosResponse) => {
            if (response.status == 204) {
              this.$emit("comment:delete", this.comment)
            }
            this.deleteDialogVisible = false;
          })
          .catch(
              (error: AxiosError) => this.error = getVerboseAxiosError(error)
          )
    },
    updateComment() {
      api.put("/comments/" + this.comment.id, {text: this.commentText})
          .then(
              (response: AxiosResponse) => {
                if (response.status == 200) {
                  this.editMode = false;
                  this.$emit("comment:update", this.comment)
                }
              }
          )
          .catch(
              (error: AxiosError) => this.error = getVerboseAxiosError(error)
          )
    }
  },
})
</script>
