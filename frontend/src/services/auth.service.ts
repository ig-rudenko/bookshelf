import api from "./api";
import TokenService from "./token.service";
import {LoginUser, RegisterUser, UserTokens} from "@/user";
import UserService from "@/services/user.service";

class AuthService {
    login(user: LoginUser) {
        return api
            .post("/auth/token", {
                username: user.username,
                password: user.password
            })
            .then(
                response => {
                    if (response.data.accessToken) {
                        TokenService.setUser(new UserTokens(response.data.accessToken, response.data.refreshToken || null));
                    }
                    return response.data
                },
                reason => {
                    console.log(reason)
                    return reason
                }
            );
    }

    logout() {
        TokenService.removeUser();
        UserService.removeUser();
    }

    register(user: RegisterUser) {
        return api.post("/auth/register", {
            username: user.username,
            email: user.email,
            password: user.password
        });
    }
}

export default new AuthService();