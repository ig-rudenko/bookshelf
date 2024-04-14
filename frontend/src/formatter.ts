function formatBytes(bytes: number, decimals = 2): string {
    if (!+bytes) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

function verboseDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {})
}

export {formatBytes, verboseDate}
