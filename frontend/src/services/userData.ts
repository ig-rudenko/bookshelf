import api from "@/services/api.ts";
import {AxiosResponse} from "axios";

export class PdfHistory {
    constructor(
        public bookId: number,
        public history: string = "",
    ) {}

    async getFromRemote() {
        this._setPdfHistory("")
        await api.get(`/user-data/book/${this.bookId}/pdf-history`).then(
            (value: AxiosResponse<{pdfHistory: string}>) => {
                if (value.status == 200) { this._setPdfHistory(value.data.pdfHistory) }
                return value.data.pdfHistory;
            }
        ).catch(error => console.log(error));
    }

    checkLocalChanges() {
        const localHistory = localStorage.getItem("pdfjs.history");
        if (localHistory !== null && localHistory !== this.history) this._pushToRemote(localHistory);
    }

    private _pushToRemote(localHistory: string) {
        api.put(`/user-data/book/${this.bookId}/pdf-history`, {pdfHistory: localHistory}).then(
            (value: AxiosResponse<{pdfHistory: string}>) => {
                if (value.status == 200) {
                    this._setPdfHistory(value.data.pdfHistory)
                } else {
                    this._setPdfHistory("");
                }
            }
        ).catch(error => console.log(error));
    }

    private _setPdfHistory(pdfHistory: string) {
        this.history = pdfHistory;
        localStorage.setItem("pdfjs.history", pdfHistory)
    }

}