<template>
    <section
        class="bookshelf-row relative my-4 w-full min-w-0 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 p-3 sm:p-4"
        :aria-labelledby="'bookshelf-name-' + bookshelf.id"
    >
        <div class="shelf-heading flex flex-wrap items-center justify-between gap-3 px-2">
            <div class="min-w-0 flex-1">
                <h2 :id="'bookshelf-name-' + bookshelf.id" class="text-lg font-semibold break-words">
                    {{ bookshelf.name }}
                </h2>
                <div class="flex flex-wrap items-center gap-3 mt-1 text-sm text-surface-600 dark:text-surface-400">
                    <span>Книг: {{ bookshelf.books.length }}</span>
                    <span v-if="bookshelf.private"><i class="pi pi-lock mr-1" aria-hidden="true" /> Приватная</span>
                </div>
            </div>
            <div class="flex items-center gap-1">
                <div class="flex items-center relative">
                    <Button
                        icon="pi pi-share-alt"
                        size="small"
                        @click="copyClipboard"
                        aria-label="Скопировать ссылку на полку"
                        text
                        severity="secondary"
                    />
                    <Badge v-if="copyClipboardText" class="text-xs absolute" style="top: -25px">{{
                        copyClipboardText
                    }}</Badge>
                </div>

                <template v-if="user?.id == bookshelf.userId">
                    <Button
                        @click="goToEditBookshelfPage"
                        icon="pi pi-pencil"
                        aria-label="Редактировать полку"
                        size="small"
                        text
                        severity="secondary"
                    />
                    <Button
                        @click="showDeleteDialog = true"
                        icon="pi pi-trash"
                        aria-label="Удалить полку"
                        size="small"
                        text
                        severity="danger"
                    />
                </template>
            </div>
        </div>

        <p v-if="bookshelf.description" class="px-2 mt-2 text-sm text-surface-600 dark:text-surface-400">
            {{ bookshelf.description }}
        </p>

        <div :id="'bookshelf-' + bookshelf.id">
            <BookshelfImages @maximize="processMaximizeChange" :books="bookshelf.books" />
        </div>
    </section>

    <Dialog
        v-model:visible="showDeleteDialog"
        modal
        header="Вы уверены, что хотите удалить книжную полку"
        :style="{ width: 'min(25rem, calc(100vw - 2rem))' }"
    >
        <div class="flex justify-end gap-2">
            <Button type="button" label="Нет" autofocus severity="secondary" @click="showDeleteDialog = false"></Button>
            <Button type="button" label="Удалить" severity="danger" @click="deleteBookshelf"></Button>
        </div>
    </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import bookshelvesService, { Bookshelf } from "@/services/bookshelves.ts";
import BookshelfImages from "@/components/BookshelfImages.vue";
import { mapState } from "vuex";

export default defineComponent({
    name: "BookshelfRow",
    components: { BookshelfImages },
    props: {
        bookshelf: { required: true, type: Object as PropType<Bookshelf> },
    },
    data() {
        return {
            showDeleteDialog: false,
            copyClipboardText: "",
        };
    },
    computed: {
        ...mapState({
            loggedIn: (state: any) => state.auth.status.loggedIn,
            user: (state: any) => state.auth.user,
        }),
    },
    methods: {
        goToEditBookshelfPage() {
            location.href = "/bookshelves/" + this.bookshelf.id + "/edit";
        },
        deleteBookshelf() {
            bookshelvesService
                .deleteBookshelf(this.bookshelf.id)
                .then(() => (location.href = "/bookshelves/"))
                .catch(() => (location.href = "/bookshelves/"));
            this.showDeleteDialog = false;
        },

        processMaximizeChange(status: string) {
            location.hash = "";
            if (status) {
                location.hash = "bookshelf-" + this.bookshelf.id;
            } else {
                location.hash = "bookshelf-name-" + this.bookshelf.id;
            }
        },

        copyClipboard() {
            navigator.clipboard
                .writeText(location.origin + "/bookshelves?search=" + this.bookshelf.name)
                .then(() => (this.copyClipboardText = "Скопировано!"))
                .catch(() => (this.copyClipboardText = "Не удалось скопировать!"));
            setTimeout(() => (this.copyClipboardText = ""), 700);
        },
    },
});
</script>

<style scoped>
@media (width >= 40rem) {
    .shelf-heading {
        padding-right: 11rem;
    }
    .bookshelf-row :deep(.bookshelf-controls) {
        position: absolute;
        top: 1rem;
        right: 1rem;
        margin-top: 0;
        padding: 0;
    }
}
</style>
