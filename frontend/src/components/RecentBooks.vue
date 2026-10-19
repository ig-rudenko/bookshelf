<script lang="ts">
import { defineComponent } from "vue";
import { Book } from "@/books";
import api from "@/services/api";
import { AxiosResponse } from "axios";
import horizontalDrag from "@/horizontalDrag";

export default defineComponent({
    name: "RecentBooks",
    mixins: [horizontalDrag],
    data() {
        return {
            recentBooks: [] as Book[],
        };
    },
    mounted() {
        this.getRecentBooks();
    },
    methods: {
        getRecentBooks() {
            api.get("/books/recent").then((res: AxiosResponse<Book[]>) => {
                this.recentBooks = res.data;
            });
        },
    },
});
</script>

<template>
    <section
        v-if="recentBooks.length"
        class="mt-6 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 p-4 sm:px-6"
        aria-labelledby="recent-books-heading"
    >
        <h2 id="recent-books-heading" class="text-base font-semibold mb-3">Последние добавленные</h2>

        <div
            class="recent-books pb-1"
            :class="{ 'is-dragging': dragging }"
            @pointerdown="startDrag"
            @pointermove="moveDrag"
            @pointerup="endDrag"
            @pointercancel="endDrag"
            @pointerleave="endDrag"
            @lostpointercapture="endDrag"
            @click.capture="clickBook"
            @dragstart.prevent
        >
            <a
                :href="'/book/' + book.id"
                v-for="book in recentBooks"
                :key="book.id"
                class="flex items-start gap-3 rounded min-w-0 group"
            >
                <img
                    alt=""
                    class="w-16 h-24 object-contain object-top shrink-0 rounded"
                    :src="book.previewImage.replace('.png', '_thumb_medium.png')"
                    loading="lazy"
                />
                <span class="min-w-0">
                    <span class="text-sm leading-5 line-clamp-3 group-hover:text-primary" :title="book.title">{{
                        book.title
                    }}</span>
                    <span
                        class="mt-1 text-xs leading-5 text-surface-600 dark:text-surface-400 line-clamp-2"
                        :title="book.authors"
                        >{{ book.authors }}</span
                    >
                </span>
            </a>
        </div>
    </section>
</template>

<style scoped>
.recent-books {
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: minmax(15rem, 1fr);
    gap: 1.5rem;
    overflow-x: auto;
    cursor: grab;
    user-select: none;
}
.recent-books.is-dragging {
    cursor: grabbing;
}
.recent-books a {
    cursor: inherit;
}
</style>
