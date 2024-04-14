const languagesList = [
    {label: "Русский", code: "ru"},
    {label: "Английский", code: "gb"}
]

function getLanguagePairByLabel(label: string) {
    for (const element of languagesList) {
        if (element.label === label) return element;
    }
    return languagesList[0];
}

export {languagesList, getLanguagePairByLabel}