class FilterBook {
    constructor(
        public search: string|null = null,
        public title: string|null = null,
        public authors: string|null = null,
        public publisher: string|null = null,
        public year: number|null = null,
        public language: string|null = null,
        public pagesGt: number|null = null,
        public pagesLt: number|null = null,
        public description: string|null = null,
        public onlyPrivate: boolean|null = null,
        public tags: string[] = [],
    ) {}

    get urlParams(): string {
        let urlParams = new URLSearchParams();
        if (this.search) urlParams.set("search", this.search);
        if (this.title) urlParams.set("title", this.title);
        if (this.authors) urlParams.set("authors", this.authors);
        if (this.publisher) urlParams.set("publisher", this.publisher);
        if (this.year) urlParams.set("year", String(this.year));
        if (this.language) urlParams.set("language", this.language);
        if (this.pagesGt) urlParams.set("pages-gt", String(this.pagesGt));
        if (this.pagesLt) urlParams.set("pages-lt", String(this.pagesLt));
        if (this.description) urlParams.set("description", this.description);
        if (this.onlyPrivate) urlParams.set("only-private", String(this.onlyPrivate));
        for (const tag of this.tags) {
            urlParams.append("tags", tag);
        }
        return urlParams.toString();
    }
}


function createFilterBook(params: any): FilterBook {
    let tags: string[]
    if (typeof params.tags === "string") {
        tags = [params.tags]
    } else {
        tags = params.tags
    }

    return new FilterBook(
        params.search,
        params.title,
        params.authors,
        params.publisher,
        params.year,
        params.language,
        params.pagesGt,
        params.pagesLt,
        params.description,
        params.onlyPrivate,
        tags,
    )
}

export { FilterBook, createFilterBook };