<template>
    <article
        class="relative min-w-0"
        :class="
            compactView
                ? 'w-28 sm:w-46'
                : 'flow-root w-full rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 p-3 sm:p-4'
        "
    >
        <div v-if="showImage" :class="compactView ? 'w-full' : 'float-left w-28 sm:w-50 mr-4 sm:mr-6 mb-2'">
            <a
                :href="'/book/' + book.id"
                @click="$emit('click:book', book, $event)"
                class="block rounded-md hover:opacity-90"
            >
                <img
                    :src="book.previewImage"
                    :alt="book.title"
                    loading="lazy"
                    class="w-full object-contain object-top rounded-md"
                    :class="imageClasses"
                />
            </a>
        </div>

        <div v-if="!compactView" class="book-card-content min-w-0">
            <h3 class="text-base sm:text-xl font-semibold leading-snug">
                <a
                    :href="'/book/' + book.id"
                    @click="$emit('click:book', book, $event)"
                    class="hover:text-primary hover:underline underline-offset-4"
                    >{{ book.title }}</a
                >
                <i v-if="book.private" class="pi pi-lock ml-2 text-sm" aria-label="Личная книга" />
            </h3>
            <p class="text-sm text-surface-700 dark:text-surface-300">{{ book.authors }}</p>
            <div class="book-metadata flex flex-wrap gap-x-3 gap-y-1 text-surface-600 dark:text-surface-400">
                <span>{{ book.year }} г.</span>
                <span>{{ book.language }}</span>
                <span>{{ book.pages }} стр.</span>
            </div>
            <p>
                <button
                    type="button"
                    @click="$emit('select:publisher', book.publisher.name)"
                    class="text-left text-sm text-primary cursor-pointer hover:underline underline-offset-4"
                >
                    {{ book.publisher.name }}
                </button>
            </p>
            <div class="pt-1">
                <button
                    type="button"
                    v-for="tag in book.tags"
                    :key="tag.id"
                    @click="selectTag(tag.name)"
                    class="inline-block align-top mr-1.5 mb-1.5 cursor-pointer rounded border border-surface-200 dark:border-surface-700 bg-surface-100 dark:bg-surface-800 px-2 py-1 text-primary text-xs leading-5 hover:border-primary"
                >
                    {{ tag.name }}
                </button>
            </div>
        </div>
    </article>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import { Book } from "@/books";
import MarkFavorite from "@/components/Bookmarks.vue";

export default defineComponent({
    name: "BookCard",
    components: { MarkFavorite },
    props: {
        book: { required: true, type: Object as PropType<Book> },
        compactView: { required: false, type: Boolean, default: false },
        showImage: { required: false, type: Boolean, default: true },
        imageClasses: {
            required: false,
            type: Object as PropType<{ [key: string]: boolean }>,
            default: () => ({ "": false }),
        },
    },
    emits: ["select:tag", "select:publisher", "click:book"],
    methods: {
        showBook() {},
        selectTag(tag: string) {
            this.$emit("select:tag", tag);
        },
    },
});
</script>

<style scoped>
.book-card-content > * + * {
    margin-top: 0.5rem;
}
</style>
