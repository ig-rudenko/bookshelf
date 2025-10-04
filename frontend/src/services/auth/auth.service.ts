import axios from "axios";

import api from "@/services/api";
import {LoginUser, RegisterUser} from "@/user";
import UserService from "@/services/auth/user.service";
import {tokenService} from "@/services/auth/token.service";

class AuthService {

    register(user: RegisterUser) {
        return api.post("/auth/users", {
            username: user.username,
            email: user.email,
            password: user.password,
            recaptchaToken: user.recaptchaToken,
        });
    }

    async login(user: LoginUser) {
        let response = await axios.post("/api/v1/auth/token", {
            username: user.username,
            password: user.password
        });
        tokenService.setTokens(response.data.accessToken, response.data.refreshToken);
        return response
    }

    logout() {
        tokenService.removeTokens();
        UserService.removeUser();
    }

}

export default new AuthService();
