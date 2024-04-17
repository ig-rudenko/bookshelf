
export class CreateBook {
    constructor(
        public title: string = "",
        public authors: string = "",
        public publisher: string = "",
        public description: string = "",
        public year: number|null = null,
        public private_: boolean = false,
        public tags: string[] = [],
        public language?: {label: string, code: string},
    ) {}
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
