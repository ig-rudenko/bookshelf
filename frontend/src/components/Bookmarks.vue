<script lang="ts">
import { defineComponent } from "vue";
import api from "@/services/api";
import { AxiosResponse } from "axios";

export default defineComponent({
    name: "MarkFavorite",
    props: {
        bookId: { required: true, type: Number },
        type: { required: true, type: String },
        mark: { required: true, type: Boolean },
    },
    emits: ["updated"],
    methods: {
        toggle() {
            if (this.mark) {
                api.delete("bookmarks/" + this.bookId + "/" + this.type).then((res: AxiosResponse) => {
                    if (res.status == 204) {
                        this.$emit("updated", false);
                    }
                });
            } else {
                api.post("bookmarks/" + this.bookId + "/" + this.type).then((res: AxiosResponse) => {
                    if (res.status == 200) {
                        this.$emit("updated", true);
                    }
                });
            }
        },
    },
});
</script>

<template>
    <div class="inline-flex items-center gap-2">
        <Button
            v-if="type == 'favorite'"
            v-tooltip.bottom="mark ? 'Убрать из избранного' : 'Добавить в избранное'"
            @click="toggle"
            :icon="mark ? 'pi pi-heart-fill' : 'pi pi-heart'"
            :aria-label="mark ? 'Убрать из избранного' : 'Добавить в избранное'"
            :aria-pressed="mark"
            :aria-describedby="'bookmark-status-' + type + '-' + bookId"
            :outlined="!mark"
            rounded
        />

        <Button
            v-if="type == 'read'"
            v-tooltip.bottom="mark ? 'Убрать из прочитанного' : 'Пометить прочитанным'"
            @click="toggle"
            :icon="mark ? 'pi pi-check' : 'pi pi-book'"
            :aria-label="mark ? 'Убрать из прочитанного' : 'Пометить прочитанным'"
            :aria-pressed="mark"
            :aria-describedby="'bookmark-status-' + type + '-' + bookId"
            :outlined="!mark"
            rounded
        />
        <span
            :id="'bookmark-status-' + type + '-' + bookId"
            role="status"
            class="text-sm text-surface-700 dark:text-surface-300"
        >
            {{ type === "favorite" ? (mark ? "В избранном" : "Не в избранном") : mark ? "Прочитано" : "Не прочитано" }}
        </span>
    </div>
</template>
