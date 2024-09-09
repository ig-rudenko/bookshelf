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

    async getBookshelvesList(page: number, searchText: string, perPage?: number): Promise<PaginatedBookshelvesResult | null> {
        let urlParams = `?page=${page}`;
        if (perPage) urlParams += `&per-page=${perPage}`;
        if (searchText) urlParams += `&search=${searchText}`;

        history.pushState({path: urlParams}, '', urlParams);

        if (this.lastUrlParams == urlParams) return null;
        this.lastUrlParams = urlParams

        return await api.get("/bookshelves" + urlParams)
            .then(
                (value: AxiosResponse<PaginatedBookshelvesResult>) => value.data
            )
    }

}


const bookshelvesService = new BookshelvesService();

export default bookshelvesService;

