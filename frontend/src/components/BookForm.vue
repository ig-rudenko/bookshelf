<template>
<div class="flex flex-wrap flex-column align-content-center">

  <div class="flex flex-wrap justify-content-center pb-3 align-items-center">
    <div id="drag-drop-area">
      <div class="flex align-content-center">
        <input ref="inputFile" id="book.file" accept="application/pdf" hidden type="file" @change="handleFileChange"/>

        <div v-if="editMode && !bookFile" class="m-2 mr-4 border-round-3xl">
          <div class="flex justify-content-center">
            <Button icon="pi pi-file-pdf" label="Обновить файл книги" @click="() => {(<HTMLInputElement>$refs.inputFile).click()}"/>
          </div>
          <div>
            <img :src="editBookPreview" class="border-round-3xl w-full" alt="preview"/>
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
        <Button v-if="editMode" severity="success" label="Обновить" @click="createBook" />
        <Button v-else-if="bookFile" severity="success" label="Создать" @click="createBook" />

        <div class="flex flex-column gap-2 pb-2 w-25rem w-full">
          <label for="book.title">Название книги</label>
          <InputText id="book.title" class="w-full" v-model="book.title"/>
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.authors">Авторы</label>
          <InputText class="w-full" id="book.authors" v-model="book.authors" />
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.publisher">Издательство</label>
          <AutoComplete input-class="w-full" id="book.authors" v-model="book.publisher" :suggestions="publishersList" @complete="searchPublishers" />
        </div>
        <div class="flex flex-column gap-2 pb-2">
          <label for="book.year">Год издания</label>
          <InputNumber input-class="w-6rem" id="book.year" v-model="book.year" suffix=" г." :useGrouping="false"/>
        </div>

        <div class="flex flex-column gap-2 pb-2">
          <label for="book.language">Язык книги</label>
          <Dropdown id="book.language" v-model="book.language" :options="languages">
            <template #option="slotProps">
              <div class="flex align-items-center">
                <img :alt="slotProps.option.label" :src="`https://flagcdn.com/${slotProps.option.code}.svg`" class="mr-2" style="width: 18px" />
                <div>{{ slotProps.option.label }}</div>
              </div>
            </template>
            <template #value="data">
              <div v-if="data.value" class="flex align-items-center">
                <img :alt="data.value.label" :src="`https://flagcdn.com/${data.value.code}.svg`" class="mr-2" style="width: 18px" />
                <div>{{ data.value.label }}</div>
              </div>
            </template>
          </Dropdown>
        </div>

        <div class="pb-2">
          <Button @click="book.private_=!book.private_"
                  :severity="book.private_?'contrast':'primary'"
                  :icon="book.private_?'pi pi-eye-slash':'pi pi-eye'"
                  :label="book.private_?'Никто не увидит вашу книгу':'Книга будет доступна всем'" class="w-full" />
        </div>

        <div class="flex flex-column gap-2 pb-2">
          <label for="book.tags">Теги</label>
          <InputGroup>
            <InputText @keydown.enter="addTag" id="book.tags" v-cloak v-model="currentTag" separator="," aria-describedby="book.tags-help" />
            <Button icon="pi pi-plus" severity="success" @click="addTag" />
          </InputGroup>
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
    <Textarea id="book.description" v-model="book.description" rows="6"/>
  </div>

</div>
</template>

<script lang="ts">
import {defineComponent} from 'vue'
import {Book, CreateBook} from "@/books";
import api from "@/services/api.ts";
import {AxiosResponse} from "axios";
import {AutoCompleteCompleteEvent} from "primevue/autocomplete";
import {getLanguagePairByLabel, languagesList} from "@/languages";

export default defineComponent({
  name: "CreateBook",
  props: {
    editBookId: {required: false, type: Number, default: 0},
  },
  data() {
      return {
        bookFile: null as (File|null),
        editBookPreview: "",
        book: new CreateBook(),
        currentTag: "",
        languages: languagesList,
        windowWidth: window.innerWidth,
        publishersList: [] as string[],
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

    createBook() {
      const data = {
        title: this.book.title,
        authors: this.book.authors,
        publisher: this.book.publisher,
        description: this.book.description,
        year: this.book.year,
        private: this.book.private_,
        language: this.book.language?.label,
        tags: this.book.tags,
      }

      if (this.editMode) {
        // Редактирование книги
        api.put(`/books/${this.editBookId}`, data)
            .then(
                (value: AxiosResponse<Book>) => {
                  if (value.status == 200 && this.bookFile) {
                    this.uploadBookFile(value.data);
                  } else if (value.status == 200) {
                    this.$router.push("/book/"+this.editBookId);
                  }
                }
            )
      } else {
        // Создание новой книги
        if (!this.bookFile) return;
        api.post("/books", data)
            .then(
                (value: AxiosResponse<Book>) => {
                  if (value.status == 201) this.uploadBookFile(value.data);
                }
            )
      }
    },

    uploadBookFile(bookData: Book) {
      const form = new FormData()
      form.append("file", (<Blob>this.bookFile))
      api.post("/books/"+bookData.id+"/upload", form, {headers: {"Content-Type": "multipart/form-data"}})
          .then(
              (value: AxiosResponse<any>) => {
                if (value.status == 200) this.$router.push("/book/"+bookData.id);
              },
          )
    },

    getEditBook() {
      api.get("/books/"+this.editBookId)
          .then(
              (response: AxiosResponse<Book>) => {
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
                    response.data.private_,
                    tags,
                    getLanguagePairByLabel(response.data.language),
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