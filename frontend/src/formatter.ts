export function formatBytes(bytes: number, decimals = 2): string {
    if (!+bytes) return '0 Bytes'
    const k: number = 1024
    const dm: number = decimals < 0 ? 0 : decimals
    const sizes: string[] = ['Б', 'КБ', 'МБ', 'ГБ']
    const i: number = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

export function verboseDate(dateString: string): string {
    const date: Date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {})
}

export function textToHtml(text: string): string {
    return text.replace(/\n/g, '<br>')
}


export function wrapLinks(text: string): string {
    let regex: RegExp = /\[([\S\s]+?)]\((https?:\/\/\S+)\)/g;
    text = text.replace(regex, '<a href="$2" class="text-primary" target="_blank">$1</a>')

    // Создаем регулярное выражение для поиска ссылок
    regex = /(?<!(\S]\()|(href="))(https?:\/\/\S+)/g;
    // Заменяем все найденные ссылки на теги <a href="...">...</a>
    return text.replace(regex, '<a href="$3" target="_blank">$3</a>')
}


export function getReadPagesCountColor(percent: number): string {
    if (percent < 20) return 'var(--p-surface-500)';
    if (percent < 50) return 'var(--p-primary-500)';
    if (percent < 90) return 'var(--p-blue-400)';
    return 'var(--p-purple-500)';
}
