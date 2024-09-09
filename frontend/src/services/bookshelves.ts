import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export interface EditBookshelf {
    name: string
    description: string
    books: number[]
}

export interface Bookshelf extends EditBookshelf {
    id: number
    createdAt: string
    userId: number
}

export interface PaginatedBookshelvesResult {
    bookshelves: Bookshelf[]
    totalCount: number
    currentPage: number
    maxPages: number
    perPage: number
}


class BookshelvesService {
    public lastUrlParams: string = "";

    async getBookshelf(id: number | string): Promise<Bookshelf> {
        let value = await api.get("/bookshelf/" + id);
        return value.data;
    }

    getBookshelvesList(page: number, searchText: string, perPage?: number): Promise<PaginatedBookshelvesResult> | null {
        let urlParams = `?page=${page}`;
        if (perPage) urlParams += `&per-page=${perPage}`;
        if (searchText) urlParams += `&search=${searchText}`;

        history.pushState({path: urlParams}, '', urlParams);

        if (this.lastUrlParams == urlParams) return null;
        this.lastUrlParams = urlParams

        return api.get("/bookshelf" + urlParams)
            .then(
                (value: AxiosResponse<PaginatedBookshelvesResult>) => value.data
            )
    }

    async createBookshelf(data: EditBookshelf): Promise<Bookshelf> {
        let value = await api.post("/bookshelf", data);
        return value.data;
    }

    async updateBookshelf(id: number | string, data: EditBookshelf): Promise<Bookshelf> {
        let value = await api.put("/bookshelf/" + id, data);
        return value.data;
    }

    deleteBookshelf(id: number | string) {
        return api.delete("/bookshelf/" + id)
    }

}


const bookshelvesService = new BookshelvesService();

export default bookshelvesService;

