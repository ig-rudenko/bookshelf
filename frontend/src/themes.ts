// On page load or when changing themes, best to add inline in `head` to avoid FOUC
function checkTheme() {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark')
    } else {
        document.documentElement.classList.remove('dark')
    }
}

export enum ThemesValues {
    light = "light",
    dark = "dark",
    auto = "auto"
}

export function getCurrentTheme(): ThemesValues {
    return localStorage.theme || "auto"
}

// Whenever the user explicitly chooses light mode
export function setLightTheme() {
    localStorage.theme = 'light'
    checkTheme()
}

// Whenever the user explicitly chooses dark mode
export function setDarkTheme() {
    localStorage.theme = 'dark'
    checkTheme()
}

// Whenever the user explicitly chooses to respect the OS preference
export function setAutoTheme() {
    localStorage.removeItem('theme')
    checkTheme()
}

checkTheme();