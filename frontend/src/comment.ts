class Comment {
    constructor(
        public id: number,
        public text: string,
        public createdAt: string,
        public user: {id: number, username: string},
    ) {}
}

class CommentResult {
    constructor(
        public comments: Comment[],
        public totalCount: number,
        public currentPage: number,
        public maxPages: number,
        public perPage: number
    ) {}
}

export {Comment, CommentResult};
