import {createNewUser, User} from "@/user";

class UserService {
    getUser(): User | null {
        const data = localStorage.getItem("user")
        if (data) {
            const jsonData = JSON.parse(data)
            return createNewUser(jsonData)
        }
        return null
    }

    setUser(user: User): void {
        localStorage.setItem("user", JSON.stringify(user));
    }

    removeUser(): void {
        localStorage.removeItem("user");
    }

}

export default new UserService();