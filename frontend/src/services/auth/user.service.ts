import api from "@/services/api";
import {createNewUser, User} from "@/user";

export async function getMyselfData(): Promise<User> {
    const resp = await api.get("auth/myself")
    return createNewUser(resp.data)
}

class UserService {
    private user: User | null = null;

    getUser(): User | null {
        if (this.user) return this.user;
        const data = localStorage.getItem("user")
        if (data) this.user = JSON.parse(data)
        return this.user;
    }

    setUser(user: User): void {
        this.user = user;
        localStorage.setItem("user", JSON.stringify(user));
    }

    removeUser(): void {
        this.user = null;
        localStorage.removeItem("user");
    }

}

export default new UserService();
