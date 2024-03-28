import axios from "axios";

const instance = axios.create({
    baseURL: "/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials: false // do not send cookies
});

export default instance;