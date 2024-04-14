<template>
  <Card class="m-1 border-1 border-100" style="max-width: 45rem; width: 100%">
    <template #subtitle>
      <div class="flex align-items-center justify-content-between text-900">
        <div class="flex align-items-center">
          <Avatar size="normal" :image="'https://ui-avatars.com/api/?size=32&name='+comment.user.username+'&font-size=0.33&background=random&rounded=true'"/>
          <span class="mx-2">{{comment.user.username}}</span>
          <div v-if="comment.user.id == user?.id">
            <Button @click="editMode = !editMode" rounded text icon="pi pi-pencil" size="small" severity="warning"/>
            <Button @click="deleteDialogVisible = true" rounded text icon="pi pi-trash" size="small" severity="danger"/>
          </div>
        </div>
        <div>
          {{verboseDate(comment.createdAt)}}
        </div>
      </div>
    </template>
    <template #content>
      <div v-if="editMode">
        <Textarea class="w-full" rows="7" v-model="commentText" />
        <Button severity="success" label="Обновить" @click="updateComment" />
      </div>
      <div v-else>
        {{comment.text}}
      </div>
    </template>
  </Card>

  <Dialog v-model:visible="deleteDialogVisible" class="pt-2" :show-header="false" modal :style="{ width: '25rem' }">
    <div class="flex align-items-center py-4">
      <i class="text-5xl pi pi-exclamation-circle mr-2" />
      <h3>Вы уверены, что хотите удалить комментарий?</h3>
    </div>

    <div class="flex justify-content-end gap-2">
      <Button type="button" severity="secondary" label="Не удалять" @click="deleteDialogVisible = false"></Button>
      <Button type="button" severity="danger" label="Удалить" @click="deleteComment"></Button>
    </div>
  </Dialog>

</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {Comment} from "@/comment";
import {verboseDate} from "../formatter";
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

<style scoped>

</style>