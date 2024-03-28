class ThemeSwitch {
    private _current: string

    constructor() {
        let themeStore = localStorage.getItem("userTheme")
        if (!themeStore) {
            themeStore = "lara-light-teal"
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
        if (theme === "lara-light-teal") {
            return  "lara-dark-teal"
        } else {
            return  "lara-light-teal"
        }
    }
}

const themeSwitch = new ThemeSwitch()

export default themeSwitch
