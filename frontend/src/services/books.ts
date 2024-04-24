import {FilterBook} from "@/filters.ts";
import api from "@/services/api.ts";
import {AxiosProgressEvent, AxiosResponse} from "axios";
import {BookWithDesc, CreateBook, PaginatedBookResult} from "@/books.ts";

class BooksService {
    public lastUrlParams: string = "";

    async getBooksList(page: number, filter: null|FilterBook=null, perPage?: number): Promise<PaginatedBookResult|null> {
        let urlParams = `?page=${page}`;
        if (perPage) urlParams += `&per-page=${perPage}`;
        if (filter?.urlParams) urlParams += `&${filter.urlParams}`;

        history.pushState({ path: urlParams }, '', urlParams);

        if (this.lastUrlParams == urlParams) return null;
        this.lastUrlParams = urlParams

        return await api.get("/books" + urlParams)
          .then(
              (value: AxiosResponse<PaginatedBookResult>) => value.data
          )
    }

    private _prepareBookData(data: CreateBook) {
        return {
            title: data.title,
            authors: data.authors,
            publisher: data.publisher,
            description: data.description,
            year: data.year,
            private: data.private,
            language: data.language,
            tags: data.tags,
      }
    }

    async createBook(data: CreateBook): Promise<BookWithDesc|null> {
        return await api.post("/books", this._prepareBookData(data))
            .then((value: AxiosResponse<BookWithDesc>) => value.data)
            .catch(() => null)
    }

    async updateBook(bookId: number, data: CreateBook): Promise<BookWithDesc|null> {
        return await api.put("/books/" + bookId, this._prepareBookData(data))
            .then((value: AxiosResponse<BookWithDesc>) => value.data)
            .catch(() => null)
    }

    async uploadBookFile(bookData: BookWithDesc, file: Blob, onUploadProgress: ((progressEvent: AxiosProgressEvent) => void)) {
      const form = new FormData()
      form.append("file", file)
      return await api.post("/books/"+bookData.id+"/upload", form,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
            onUploadProgress: onUploadProgress,
          }
      ).then((value: AxiosResponse<any>): boolean => value.status == 200).catch((): boolean => false)
    }
}

const bookService = new BooksService();

export default bookService;

