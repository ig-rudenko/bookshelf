<template>
<div class="flex flex-wrap flex-column align-content-center">

  <div v-if="loading && bookFile" class="py-5 w-full p-5">
    <MeterGroup :value="[{label: 'Загрузка файла', value: uploadProgress, color: 'primary', icon: '' }]"/>
  </div>

  <div class="flex flex-wrap justify-content-center pb-3 align-items-center">
    <div id="drag-drop-area">
      <div class="flex align-content-center">
        <input ref="inputFile" id="book.file" accept="application/pdf" hidden type="file" @change="handleFileChange"/>

        <div v-if="editMode && !bookFile" class="m-2 mr-4 border-round-3xl">
          <div class="flex justify-content-center">
            <Button icon="pi pi-file-pdf" label="Обновить файл книги" @click="() => {(<HTMLInputElement>$refs.inputFile).click()}"/>
          </div>
          <div>
            <img v-if="editBookPreview" :src="editBookPreview" class="border-round-3xl w-full" alt="preview"/>
            <div v-else class="border-round-3xl" style="padding: 18rem 15rem; background-color: rgba(204,204,204,0.09);"></div>
          </div>
        </div>

        <label v-else-if="!bookFile" for="book.file" >
          <span v-if="!isMobile" style="padding: 250px 150px" class="flex flex-column align-items-center cursor-pointer m-4 mr-4 border-1 border-purple-700 text-purple-700 hover:text-purple-300 hover:border-purple-300 border-round-3xl border-dashed">
            <i style="font-size: 3rem;" class="pi pi-file-pdf pb-2"/>
            <span>Загрузить файл</span>
          </span>
          <Button v-else icon="pi pi-file-pdf" label="Загрузить файл" @click="() => {(<HTMLInputElement>$refs.inputFile).click()}"/>
        </label>

        <div v-if="bookFile">
          <div class="flex justify-content-center">
            <Button icon="pi pi-file-pdf" :label="truncateString(bookFile?.name)" @click="() => {(<HTMLInputElement>$refs.inputFile).click()}"/>
          </div>
          <div v-if="bookPreview && !isMobile" class="px-4">
            <object style="width: 520px; height: 750px" :data="bookPreview"/>
          </div>
        </div>
      </div>


    </div>
    <div>
      <div class="flex flex-column gap-2 mt-4">
        <Button v-if="editMode && !loading" severity="success" label="Обновить" @click="createBook" />
        <Button v-else-if="bookFile && !loading" severity="success" label="Создать" @click="createBook" />
        <Button v-else-if="loading" disabled severity="success" icon="pi pi-spin pi-spinner" label="Загрузка..." />

        <div class="flex flex-column gap-2 pb-2 w-25rem w-full">
          <label for="book.title">Название книги</label>
          <InputText id="book.title" class="w-full" :class="validator.title?'':'p-invalid'" v-model="book.title"/>
          <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" v-if="!validator.title" @click="validator.validateTitle(book.title)">Укажите от 1 до 128 символов</InlineMessage>
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.authors">Авторы</label>
          <InputText class="w-full" id="book.authors" v-model="book.authors" :class="validator.authors?'':'p-invalid'" />
          <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" v-if="!validator.authors" @click="validator.validateAuthors(book.authors)">Укажите от 1 до 254 символов</InlineMessage>
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.publisher">Издательство</label>
          <AutoComplete input-class="w-full" :class="validator.publisher?'':'p-invalid'"
                        id="book.authors" v-model="book.publisher" :suggestions="publishersList" @complete="searchPublishers" />
          <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" v-if="!validator.publisher" @click="validator.validatePublisher(book.publisher)">Укажите от 1 до 128 символов</InlineMessage>
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.year">Год издания</label>
          <InputNumber input-class="w-6rem" :class="validator.year?'':'p-invalid'"
                       id="book.year" v-model="book.year" suffix=" г." :useGrouping="false" aria-describedby="book.year-help"/>
          <small id="book.year-help">Укажите год публикации оригинала</small>
          <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" v-if="!validator.year" @click="validator.validateYear(book.year)">Укажите год в пределах от 1000 до {{new Date().getFullYear()+1}}</InlineMessage>
        </div>

        <div class="flex flex-column gap-2 pb-2">
          <label for="book.language">Язык книги</label>
          <LanguageDropdown :language="book.language" @update="(l: string) => book.language=l" :class="validator.language?'':'p-invalid'"/>
          <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" v-if="!validator.language" @click="validator.validateLanguage(book.language)">Укажите от 1 до 128 символов</InlineMessage>
        </div>

        <div class="pb-2">
          <Button @click="book.private=!book.private"
                  :severity="book.private?'contrast':'primary'"
                  :icon="book.private?'pi pi-eye-slash':'pi pi-eye'"
                  :label="book.private?'Никто не увидит вашу книгу':'Книга будет доступна всем'" class="w-full" />
        </div>

        <div class="flex flex-column gap-2 pb-2">
          <label for="book.tags">Теги</label>
          <InputGroup>
            <InputText @keydown.enter="addTag" id="book.tags" v-cloak v-model="currentTag" separator="," aria-describedby="book.tags-help" />
            <Button icon="pi pi-plus" severity="success" @click="addTag" />
          </InputGroup>
          <div class="flex flex-column zoomin cursor-pointer" v-tooltip="'Проверить заново'" @click="validator.validateTags(book.tags)">
            <InlineMessage severity="error" v-if="!validator.tagsCount">Укажите от 1 до 20 тегов</InlineMessage>
            <InlineMessage severity="error" v-if="!validator.tagLength">Название тега должно быть от 1 до 128 символов</InlineMessage>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap lg:max-w-20rem">
        <Chip v-for="(tag, index) in book.tags" :key="index" :label="tag" icon="pi pi-tag" class="m-1" removable >
          <template #removeicon>
            <i @click="removeTag(index)" class="pi pi-times cursor-pointer ml-2" />
          </template>
        </Chip>
      </div>

    </div>

  </div>

  <div class="flex flex-column gap-2 pb-2">
    <label for="book.description">Описание книги</label>
    <Textarea id="book.description" v-model="book.description" rows="6" :class="validator.description?'':'p-invalid'"/>
    <InlineMessage class="zoomin cursor-pointer" v-tooltip="'Проверить заново'" severity="error" @click="validator.validateDescription(book.description)" v-if="!validator.description">Укажите описание, но не более 4096 символов</InlineMessage>
  </div>

</div>
</template>

<script lang="ts">
import {defineComponent} from 'vue';
import {AxiosProgressEvent, AxiosResponse} from "axios";
import {AutoCompleteCompleteEvent} from "primevue/autocomplete";

import api from "@/services/api";
import {BookDetail, BookValidator, BookWithDesc, CreateBook} from "@/books";
import LanguageDropdown from "@/components/LanguageDropdown.vue";
import bookService from "@/services/books.ts";

export default defineComponent({
  name: "CreateBook",
  components: {LanguageDropdown},
  props: {
    editBookId: {required: false, type: Number, default: 0},
  },
  data() {
      return {
        bookFile: null as (File|null),
        editBookPreview: "",
        book: new CreateBook(),
        validator: new BookValidator(),
        currentTag: "",
        windowWidth: window.innerWidth,
        publishersList: [] as string[],
        loading: false,
        uploadProgress: 0,
      }
  },
  mounted() {
    this.addDragAndDropListeners()
    window.addEventListener('resize', () => {
      this.windowWidth = window.innerWidth
    })

    if (this.editBookId > 0) {
      this.getEditBook()
    }

  },

  computed: {
    isMobile() {
      return this.windowWidth <= 768
    },
    bookPreview(): string {
      if (!this.bookFile) return ""
      return URL.createObjectURL(this.bookFile);
    },
    editMode(): boolean {
      return this.editBookId > 0;
    }
  },

  methods: {
    addTag() {
      if (this.currentTag.length > 0 && !this.book.tags.includes(this.currentTag)) {
        this.book.tags.push(this.currentTag);
        this.currentTag = "";
        this.validator.validateTags(this.book.tags)
      }
    },
    removeTag(index: number) {
      this.book.tags.splice(index, 1);
    },

    searchPublishers(event: AutoCompleteCompleteEvent) {
      api.get("/books/publishers?name="+event.query)
          .then(
              (value: AxiosResponse<string[]>) => {
                this.publishersList = value.data;
              }
          )
    },

    addDragAndDropListeners(): void {
      let container = document.querySelector("#drag-drop-area")!;
      container.addEventListener("dragover", e => e.preventDefault());
      container.addEventListener("drop", (e) => this.addByDragAndDrop(<DragEvent>e));
    },

    addByDragAndDrop(e: DragEvent): void {
      e.preventDefault();
      if (e.dataTransfer) {
        this.bookFile = e.dataTransfer.files[0]
      }
    },
    handleFileChange(event: Event): void {
      let files = (<HTMLInputElement>event.target).files
      if (files && files.length > 0) {
        this.bookFile = files[0]
      }
    },

    truncateString(str: string) {
      const maxLength = 40;
      // Проверяем, нужно ли укорачивать строку
      if (str.length <= maxLength) {
        return str; // Строка короче или равна максимальной длине
      }

      // Длина строки, за вычетом длины троеточий (3 символа)
      const trimmedLength = maxLength - 3;

      // Вычисляем начальную и конечную части строки
      const start = str.slice(0, Math.ceil(trimmedLength / 2)); // Начальная часть
      const end = str.slice(str.length - Math.floor(trimmedLength / 2)); // Конечная часть

      // Собираем укороченную строку с троеточиями в середине
      return `${start}...${end}`;
    },

    async createBook() {
      this.validator.validate(this.book)
      if (!this.validator.isValid) return;

      if (this.editMode) {
        // Редактирование книги
        this.loading = true;
        const book = await bookService.updateBook(this.editBookId, this.book)
        if (book && this.bookFile) {
          await this.uploadBookFile(book)
        } else {
          document.location.href = "/book/"+this.editBookId;
        }
        this.loading = false;

      } else {
        // Создание новой книги
        if (!this.bookFile) return;
        this.loading = true;
        const book = await bookService.createBook(this.book)
        if (book) {
          await this.uploadBookFile(book);
        }
        this.loading = false;
      }
    },

    async uploadBookFile(bookData: BookWithDesc) {
      const status = await bookService.uploadBookFile(bookData, (<Blob>this.bookFile), this.onUploadProgress);
      if (status) document.location.href = "/book/"+(this.editBookId||bookData.id);
    },

    onUploadProgress(progressEvent: AxiosProgressEvent) {
      this.uploadProgress = (progressEvent.progress||0) * 100;
    },

    getEditBook() {
      api.get("/books/"+this.editBookId)
          .then(
              (response: AxiosResponse<BookDetail>) => {
                if (response.status !== 200) return;
                const tags = []
                for (const tag of response.data.tags) {
                  tags.push(tag.name)
                }
                this.book = new CreateBook(
                    response.data.title,
                    response.data.authors,
                    response.data.publisher.name,
                    response.data.description,
                    response.data.year,
                    response.data.private,
                    tags,
                    response.data.language,
                );
                this.editBookPreview = response.data.previewImage;
              }
          )
    }

  }
});
</script>

<style scoped>

</style>