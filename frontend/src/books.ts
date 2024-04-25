
export class CreateBook {
    constructor(
        public title: string = "",
        public authors: string = "",
        public publisher: string = "",
        public description: string = "",
        public year: number|null = null,
        public private_: boolean = false,
        public tags: string[] = [],
        public language: string|null = null,
    ) {}

    get private(): boolean {
        return this.private_;
    }

    set private(value: boolean) {
        this.private_ = value;
    }
}


export class BookValidator {
    private _isValid: boolean = true;

    constructor(
        public title: boolean = true,
        public authors: boolean = true,
        public publisher: boolean = true,
        public description: boolean = true,
        public year: boolean = true,
        public private_: boolean = true,
        public tagsCount: boolean = true,
        public tagLength: boolean = true,
        public language: boolean = true,
    ) {}

    validateTitle(title: string) {
        this.title = title.length > 0 && title.length < 100;
    }

    validateAuthors(authors: string) {
        this.authors = authors.length > 0 && authors.length < 254;
    }

    validatePublisher(publisher: string) {
        this.publisher = publisher.length > 0 && publisher.length < 128;
    }

    validateDescription(description: string) {
        this.description = description.length > 0 && description.length < 4096;
    }

    validateYear(year: number|null) {
        this.year = year !== null && year >= 1000 && year <= new Date().getFullYear() + 1;
    }

    validateTags(tags: string[]) {
        this.tagsCount = tags.length > 0 && tags.length <= 20;
        for (const tag of tags) {
            if (tag.length > 128 || tag.length == 0) {
                this.tagLength = false;
                return
            }
        }
        this.tagLength = true;
    }

    validateLanguage(language: string|null) {
        this.language = language !== null && language.length > 0 && language.length < 128;
    }

    validate(book: CreateBook) {
        this.validateTitle(book.title)
        this.validateAuthors(book.authors)
        this.validatePublisher(book.publisher)
        this.validateDescription(book.description)
        this.validateYear(book.year)
        this.validateTags(book.tags)
        this.validateLanguage(book.language)
        this._isValid = this.title && this.authors && this.description && this.publisher && this.year && this.tagsCount && this.tagLength && this.language;
    }

    get isValid(): boolean {
        return this._isValid
    }
}



export interface Book {
    id: number
    userId: number
    title: string
    previewImage: string
    authors: string
    pages: number
    size: number
    year: number
    private: boolean
    language: string
    tags: {id: number, name: string}[]
    publisher: {id: number, name: string}
}

export interface BookWithDesc extends Book {
    description: string
}

export interface BookDetail extends Book {
    description: string
    favorite: boolean
    read: boolean
}

export interface BookWithReadPages extends Book {
    readPages: number
}


export interface PaginatedBookResult {
    books: Book[],
    totalCount: number,
    currentPage: number,
    maxPages: number,
    perPage: number
}

export interface BookWithReadPagesPaginatedResult extends PaginatedBookResult{
    books: BookWithReadPages[],
}