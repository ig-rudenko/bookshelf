export function validateUsername(value: string): string {
    if (value.length <= 3) {
        return "Укажите более 3 символов"
    }
    return ""
}

export function validatePassword(value: string): string {
    if (value.length < 8) {
        return "Пароль должен быть 8 или более символов"
    }
    if (!value.match(/\d/) || !value.match(/\D/)) {
        return "Пароль должен состоять, как минимум, из цифр и букв"
    }
    return ""
}


export function validateEmail(value: string): string {
    if (!value.match(/^[A-Z0-9._%+-]+@[A-Z0-9-]+.+\.[A-Z]{2,4}$/i)) {
        return "Укажите верный адрес";
    }
    return "";
}

export function validateTwoPasswords(val1: string, val2: string): string {
    if (val1 !== val2) {
        return "Пароли не совпадают";
    }
    return validatePassword(val1);
}
