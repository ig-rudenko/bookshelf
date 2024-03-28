import AuthService from '../services/auth.service.js';
import UserService from "../services/user.service";
import TokenService from "@/services/token.service";
import {createNewUser, LoginUser, RegisterUser, User, UserTokens} from "@/user";
import api from "@/services/api";

class Status {
    constructor(
        public loggedIn: boolean,
    ) {}
}

class UserState {
    constructor(
        public status: Status,
        public user: User | null,
        public userTokens: UserTokens,
    ) {}
}

const user = UserService.getUser()
const initialState = new UserState(
    new Status(user !== null),
    user,
    TokenService.getUserTokens(),
)


export const auth = {
    namespaced: true,
    state: initialState,
    actions: {
        login({ commit }: any, user: LoginUser) {
            return AuthService.login(user).then(
                user => {
                    commit('loginSuccess');
                    return Promise.resolve(user);
                },
                error => {
                    commit('loginFailure');
                    return Promise.reject(error);
                }
            );
        },
        logout({ commit }: any) {
            AuthService.logout();
            commit('logout');
        },
        register({ commit }: any, user: RegisterUser) {
            return AuthService.register(user).then(
                response => {
                    commit('registerSuccess');
                    return Promise.resolve(response.data);
                },
                error => {
                    commit('registerFailure');
                    return Promise.reject(error);
                }
            );
        },
        refreshToken({ commit }: any, accessToken: string) {
            commit('refreshToken', accessToken);
        }
    },
    mutations: {
        loginSuccess(state: UserState) {
            state.status.loggedIn = true;
            api.get("/users/myself")
                .then(
                    resp => {
                        const user = createNewUser(resp.data)
                        UserService.setUser(user)
                        state.user = user
                        state.userTokens = TokenService.getUserTokens()
                    }
                )
        },
        loginFailure(state: UserState) {
            state.status.loggedIn = false;
            state.user = null;
        },
        logout(state: UserState) {
            state.status.loggedIn = false;
            state.user = null;
        },
        registerSuccess(state: UserState) {
            state.status.loggedIn = false;
        },
        registerFailure(state: UserState) {
            state.status.loggedIn = false;
        },
        refreshToken(state: UserState, accessToken: string) {
            state.status.loggedIn = true;
            state.userTokens.accessToken = accessToken;
        }
    }
};