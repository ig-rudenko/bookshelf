import {AxiosError} from "axios";

function getVerboseAxiosError(error: AxiosError<any>): string {
    if (error.response?.data?.detail && [400, 422].indexOf(error.response.status) != -1) {
        const detail = error.response.data.detail

        if (typeof detail[0] === "string") return detail;
        if (typeof detail[0] === "object") {
            let validationErrors = ""
            for (const detailElement of detail) {
                validationErrors += detailElement.loc[1].toString() + ": " + detailElement.msg.toString() + "<br>"
            }
            return validationErrors
        }

    }
    return error.message
}


export default getVerboseAxiosError
