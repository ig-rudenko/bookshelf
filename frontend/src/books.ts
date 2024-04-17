
class CreateBook {
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


class Book {
    constructor(
        public id: number,
        public userId: number,
        public title: string,
        public previewImage: string,
        public authors: string,
        public description: string,
        public pages: number,
        public size: number,
        public year: number,
        public private_: boolean,
        public favorite: boolean,
        public read: boolean,
        public language: string,
        public tags: {id: number, name: string}[],
        public publisher: {id: number, name: string},
    ) {}

    get private() {
        return this.private_;
    }
}


export { CreateBook, Book };