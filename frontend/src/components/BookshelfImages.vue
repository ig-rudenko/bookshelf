<template>
    <div class="bookshelf-controls flex justify-end mt-3 px-2">
        <Button
            v-if="maximize"
            @click="() => changeMaximize(false)"
            :aria-expanded="true"
            icon="pi pi-angle-double-up"
            label="Свернуть полку"
            severity="secondary"
            outlined
            size="small"
        />
        <Button
            v-else
            @click="() => changeMaximize(true)"
            :aria-expanded="false"
            icon="pi pi-angle-double-down"
            label="Развернуть полку"
            severity="secondary"
            outlined
            size="small"
        />
    </div>

    <!--Подсказка-->
    <div class="sticky z-1">
        <div v-if="!isMobile && maximize" class="absolute flex items-center left-0 p-4 text-400 text-xs top-0">
            <span class="pr-1">Листайте вправо с зажатым</span>
            <Button outlined style="padding: 2px; font-size: 12px">Shift</Button>
        </div>
    </div>

    <div
        v-if="books.length"
        class="p-5 my-4 bookshelf relative"
        :style="bookshelfStyle"
        :class="{ 'is-draggable': !maximize, 'is-dragging': dragging }"
        @pointerdown="startShelfDrag"
        @pointermove="moveShelfDrag"
        @pointerup="endDrag"
        @pointercancel="endDrag"
        @pointerleave="endDrag"
        @lostpointercapture="endDrag"
        @click.capture="clickBook"
        @dragstart="!maximize && $event.preventDefault()"
    >
        <!--Обложки книг-->
        <div v-for="book in books" :key="book.id" class="inline-block relative book-block" :style="bookBlockStyle">
            <div
                class="absolute image-block flex flex-row"
                @mouseenter="showDetails($event, book.id)"
                @mouseleave="hideDetails"
            >
                <!--Картинка книги-->
                <a
                    :href="'/book/' + book.id"
                    @click="$emit('click:book', book, $event)"
                    @focus="showDetails($event, book.id)"
                >
                    <img
                        :src="book.preview"
                        class="book-image"
                        :style="bookImageStyle"
                        :alt="viewedBooks.get(book.id)?.title || 'Книга ' + book.id"
                    />
                </a>
            </div>
        </div>
    </div>
    <Popover
        ref="bookDetails"
        class="w-[min(28rem,calc(100vw-2rem))] max-h-[70vh] overflow-y-auto"
        @mouseenter="keepDetails"
        @mouseleave="hideDetails"
    >
        <BookCard
            v-if="currentBook"
            :book="currentBook"
            :show-image="false"
            class="!border-0 !p-0 !bg-transparent whitespace-normal"
        />
    </Popover>
</template>

<script lang="ts">
import { defineComponent, nextTick, PropType } from "vue";
import BookCard from "@/components/BookCard.vue";
import { Book } from "@/books.ts";
import api from "@/services/api";
import horizontalDrag from "@/horizontalDrag";

export default defineComponent({
    name: "BookshelfImages",
    mixins: [horizontalDrag],
    components: { BookCard },
    props: {
        books: { required: true, type: Object as PropType<{ id: number; preview: string }[]> },
    },
    emits: ["click:book", "maximize"],
    data() {
        return {
            bookImages: [] as { id: number; src: string }[],
            viewedBooks: new Map() as Map<number, Book>,
            currentBook: undefined as Book | undefined,
            windowWidth: window.innerWidth,
            maximize: false,
            detailsBookId: null as number | null,
            hideDetailsTimer: undefined as ReturnType<typeof setTimeout> | undefined,
        };
    },

    mounted() {
        window.addEventListener("resize", () => (this.windowWidth = window.innerWidth));
    },
    beforeUnmount() {
        clearTimeout(this.hideDetailsTimer);
        this.detailsBookId = null;
    },

    computed: {
        isMobile() {
            return this.windowWidth <= 768;
        },

        bookBlockStyle() {
            if (this.maximize) {
                return {
                    padding: "1rem",
                    width: "10rem !important",
                    margin: "1rem !important",
                };
            }
            return {};
        },

        bookshelfStyle() {
            if (this.maximize) {
                return {
                    "white-space": "pre-wrap !important",
                    padding: "3rem !important",
                };
            }
            return {};
        },

        bookImageStyle() {
            if (this.maximize) {
                return {
                    transform: "rotate3d(1, 1, 1, -1deg)",
                };
            }
            return {};
        },
    },

    methods: {
        startShelfDrag(event: PointerEvent) {
            if (!this.maximize) this.startDrag(event);
        },
        moveShelfDrag(event: PointerEvent) {
            this.moveDrag(event);
            if (this.dragging) {
                clearTimeout(this.hideDetailsTimer);
                this.detailsBookId = null;
                (<any>this.$refs.bookDetails).hide();
            }
        },
        async showDetails(event: Event, bookID: number) {
            if (this.dragging) return;
            this.keepDetails();
            this.detailsBookId = bookID;
            const target = event.currentTarget;
            try {
                let book = this.viewedBooks.get(bookID);
                if (!book) {
                    const response = await api.get<Book>(`/books/${bookID}`);
                    book = response.data;
                    this.viewedBooks.set(bookID, book);
                }
                if (this.detailsBookId !== bookID) return;
                const popover = <any>this.$refs.bookDetails;
                popover.hide();
                this.currentBook = book;
                await nextTick();
                if (this.detailsBookId === bookID) popover.show(event, target);
            } catch {
                if (this.detailsBookId === bookID) this.detailsBookId = null;
            }
        },
        keepDetails() {
            clearTimeout(this.hideDetailsTimer);
        },
        hideDetails() {
            this.detailsBookId = null;
            this.hideDetailsTimer = setTimeout(() => (<any>this.$refs.bookDetails).hide(), 150);
        },

        changeMaximize(status: boolean) {
            this.endDrag();
            this.dragged = false;
            this.maximize = status;
            this.$emit("maximize", this.maximize);
        },
    },
});
</script>

<style scoped>
.bookshelf {
    width: 100%;
    overflow-x: auto;
    white-space: nowrap;
    overflow-y: auto;
    border: none;
    border-bottom: 3px solid var(--p-content-border-color);
    border-radius: 0;
}

.book-block {
    min-height: 230px;
    width: 9rem !important;
}

.bookshelf.is-draggable {
    cursor: grab;
    user-select: none;
}
.bookshelf.is-dragging {
    cursor: grabbing;
}
.bookshelf.is-draggable a,
.bookshelf.is-draggable .book-image {
    cursor: inherit;
}

.book-image {
    border-radius: 0.75rem !important;
    max-height: 230px;
    min-height: 230px;
    max-width: 250px;
    margin-top: 5px;
    box-shadow: -6px -2px 2px #959595;
    border-left: 1px solid #959595;
    border-bottom: 1px solid #959595;
    cursor: pointer;
}

/* При наведении на обложку поднимаем её на передний план */
.image-block:hover,
.image-block:active,
.image-block:focus-within {
    z-index: 2;
}

/* Увеличение книги при наведении на обложку */
.image-block:hover .book-image {
    transform: scale(1.15) !important;
    box-shadow: 0 0 5px #121212;
}

@media (width < 768px) {
    .bookshelf {
        width: 100%;
        border-radius: 0;
    }
}
</style>
