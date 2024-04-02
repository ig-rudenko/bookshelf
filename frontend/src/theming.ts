class ThemeSwitch {
    private _current: string

    constructor() {
        let themeStore = localStorage.getItem("userTheme")
        if (!themeStore) {
            themeStore = "soho-light"
        }
        this._current = themeStore
    }

    public get current(): string {
        return this._current
    }

    public get other(): string {
        return this.getOtherTheme(this._current)
    }

    toggle() {
        this._current = this.other
        localStorage.setItem("userTheme", this._current)
    }

    private getOtherTheme(theme: string) {
        if (theme === "soho-light") {
            return "soho-dark"
        } else {
            return "soho-light"
        }
    }
}

const themeSwitch = new ThemeSwitch()

export default themeSwitch
