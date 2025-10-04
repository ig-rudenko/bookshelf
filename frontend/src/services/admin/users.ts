import api from "@/services/api";


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
    recentlyReadCount: number;
}

export interface UserDetailPaginatedResult {
    results: UserDetail[],
    totalCount: number,
    currentPage: number,
    maxPages: number,
    perPage: number
}

class UsersService {

    async getAllUsersList(page: number = 0, perPage?: number, sortBy?: string, sortDirection?: number): Promise<UserDetailPaginatedResult | null> {
        let params: any = {
            "page": page,
            "per-page": perPage,
        };
        if (sortBy && sortDirection) {
            params = {
                ...params,
                "sort-by": sortBy,
                "sort-order": sortDirection > 0 ? "asc" : "desc",
            }
        }

        try {
            const resp = await api.get<UserDetailPaginatedResult>("/admin/users", {
                params: params
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
