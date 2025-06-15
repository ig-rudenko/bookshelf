import api from "@/services/api.ts";


export interface UserDetail {
    id: number;
    username: string;
    isSuperuser: boolean;
    isStaff: boolean;
    firstName: string | null;
    lastName: string | null;
    email: string;
    dateJoin: string;
    favoritesCount: number;
    readCount: number;
}

export interface UserDetailPaginatedResult {
    results: UserDetail[],
    totalCount: number,
    currentPage: number,
    maxPages: number,
    perPage: number
}

class UsersService {

    async getAllUsersList(page: number = 0, perPage?: number) {
        try {
            const resp = await api.get<UserDetailPaginatedResult>("/admin/users", {
                params: {
                    "page": page,
                    "per-page": perPage
                }
            });
            return resp.data;
        } catch (error) {
            console.error(error);
            return null
        }
    }

}

const usersService = new UsersService();
export {usersService};
