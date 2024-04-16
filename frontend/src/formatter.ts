function formatBytes(bytes: number, decimals = 2): string {
    if (!+bytes) return '0 Bytes'
    const k: number = 1024
    const dm: number = decimals < 0 ? 0 : decimals
    const sizes: string[] = ['Б', 'КБ', 'МБ', 'ГБ']
    const i: number = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

function verboseDate(dateString: string): string {
    const date: Date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {})
}

function textToHtml(text: string): string {
    return text.replace(/\n/g, '<br>')
}

export {formatBytes, verboseDate, textToHtml}
