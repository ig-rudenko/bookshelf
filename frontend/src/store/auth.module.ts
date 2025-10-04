import AuthService from '../services/auth/auth.service';
import UserService from "../services/user.service";
import {tokenService} from "@/services/auth/token.service";
import {LoginUser, RegisterUser, User, UserTokens} from "@/user";
import {getMyselfData} from "@/services/auth/user.service.ts";

class Status {
    constructor(
        public loggedIn: boolean,
    ) {
    }
}

class UserState {
    constructor(
        public status: Status,
        public user: User | null,
        public userTokens: UserTokens,
    ) {
    }
}

const user = UserService.getUser()
const initialState = new UserState(
    new Status(user !== null && user.username?.length > 0),
    user,
    tokenService.getUserTokens(),
)


export const auth = {
    namespaced: true,
    state: initialState,
    actions: {
        login({commit}: any, user: LoginUser) {
            return AuthService.login(user).then(
                (data) => {
                    if (data.status == 200) {
                        commit('loginSuccess');
                    }
                    return Promise.resolve(data);
                },
                error => {
                    commit('loginFailure');
                    return Promise.reject(error);
                }
            );
        },
        logout({commit}: any) {
            AuthService.logout();
            commit('logout');
        },
        register({commit}: any, user: RegisterUser) {
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
        refreshToken({commit}: any, tokens: any) {
            commit('refreshToken', tokens);
        }
    },
    mutations: {
        loginSuccess(state: UserState) {
            state.status.loggedIn = true;
            getMyselfData().then(
                user => {
                    UserService.setUser(user)
                    state.user = user
                    state.userTokens = tokenService.getUserTokens()
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
        refreshToken(state: UserState, accessToken: string, refreshToken: string) {
            state.status.loggedIn = true;
            state.userTokens.accessToken = accessToken;
            state.userTokens.refreshToken = refreshToken;
        }
    }
};
