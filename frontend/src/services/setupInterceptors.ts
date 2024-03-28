import axiosInstance from "./api";
import TokenService from "./token.service";

const setup = (store: any) => {
    axiosInstance.interceptors.request.use(
        (config) => {
            const token = TokenService.getLocalAccessToken();
            if (token) {
                config.headers["Authorization"] = 'Bearer ' + token;
            }
            return config;
        },
        (error) => {
            return Promise.reject(error);
        }
    );

    axiosInstance.interceptors.response.use(
        (res) => {
            return res;
        },
        async (err) => {
            const originalConfig = err.config;

            if ((originalConfig.url !== "/api/v1/auth/login" || originalConfig.url !== "/api/v1/auth/register") && err.response) {
                // Access Token was expired
                if (err.response.status === 401 && !originalConfig._retry) {
                    originalConfig._retry = true;

                    try {
                        const refreshToken = TokenService.getLocalRefreshToken()
                        if (!refreshToken) return;
                        const rs = await axiosInstance.post(
                            "auth/token/refresh",
                            { refreshToken: refreshToken },
                            originalConfig
                        );

                        if (rs.status !== 200) {
                            store.dispatch("auth/logout")
                            return rs
                        }

                        const { accessToken } = rs.data;

                        store.dispatch('auth/refreshToken', accessToken);
                        TokenService.updateLocalAccessToken(accessToken);

                        return axiosInstance(originalConfig);
                    } catch (_error) {
                        localStorage.removeItem("user")
                        return Promise.reject(_error);
                    }
                }
            }

            return Promise.reject(err);
        }
    );
};

export default setup;