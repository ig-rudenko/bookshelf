import { auth } from "./auth.module";
import {createStore} from "vuex";

const store = createStore({
    modules: {
        auth,
    },
});

export default store;