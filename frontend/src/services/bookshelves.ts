import api from "@/services/api.ts";
import {FilterBookshelf} from "@/filters.ts";

export interface EditBookshelf {
    name: string
    description: string
    private: boolean
    books: { id: number; preview: string }[]
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

    async getBookshelvesList(page: number, filter: FilterBookshelf, perPage?: number): Promise<PaginatedBookshelvesResult | null> {
        let urlParams = `?page=${page}`;
        if (perPage) urlParams += `&per-page=${perPage}`;
        urlParams += `&${filter.urlParams}`;

        history.pushState({path: urlParams}, '', urlParams);

        if (this.lastUrlParams == urlParams) return null;
        this.lastUrlParams = urlParams

        let value = await api.get("/bookshelf" + urlParams);
        return value.data;
    }

    async createBookshelf(data: EditBookshelf): Promise<Bookshelf> {
        let value = await api.post("/bookshelf", this.createBookshelfData(data));
        return value.data;
    }

    async updateBookshelf(id: number | string, data: EditBookshelf): Promise<Bookshelf> {
        let value = await api.put("/bookshelf/" + id, this.createBookshelfData(data));
        return value.data;
    }

    private createBookshelfData(data: EditBookshelf) {
        return {
            name: data.name,
            description: data.description,
            books: data.books.map(b => b.id),
            private: data.private
        }
    }

    deleteBookshelf(id: number | string) {
        return api.delete("/bookshelf/" + id)
    }

}


const bookshelvesService = new BookshelvesService();

export default bookshelvesService;

