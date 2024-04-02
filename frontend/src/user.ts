

class LoginUserIsValid {
    username: boolean = true
    usernameError: string = ""
    password: boolean = true
    passwordError: string = ""

    validateUsername(value: string): void {
        if (value.length <= 3) {
            this.username = false;
            this.usernameError = "Укажите более 3 символов";
            return;
        }
        this.username = true;
        this.usernameError = "";
    }

    validatePassword(value: string): void {
        if (value.length < 8) {
            this.password = false;
            this.passwordError = "Пароль должен быть 8 или более символов";
            return;
        }
        if (!value.match(/\d/) || !value.match(/\D/)) {
            this.password = false;
            this.passwordError = "Пароль должен состоять, как минимум, из цифр и букв";
            return;
        }
        this.password = true;
        this.passwordError = "";
    }

    get isValid(): boolean {
        return this.username && this.password;
    }

}

class RegisterUserIsValid extends LoginUserIsValid {
    email: boolean = true
    emailError: string = ""

    validateEmail(value: string): void {
        if (!value.match(/^[A-Z0-9._%+-]+@[A-Z0-9-]+.+\.[A-Z]{2,4}$/i)) {
            this.email = false;
            this.emailError = "Укажите верный адрес";
            return;
        }
        this.email = true;
        this.emailError = "";
    }

    validatePasswordPair(pass1: string, pass2: string) {
        this.validatePassword(pass1)
        if (pass1 !== pass2) {
            this.password = false;
            this.passwordError += "Пароли не совпадают";
        }
    }

    get isValid(): boolean {
        return this.username && this.password && this.email;
    }
}



class LoginUser {
    username: string = ""
    password: string = ""
    readonly valid: LoginUserIsValid

    constructor() {
        this.valid = new LoginUserIsValid()
    }

    public get isValid(): boolean {
        this.valid.validateUsername(this.username)
        this.valid.validatePassword(this.password)
        return this.valid.isValid
    }

}

class RegisterUser extends LoginUser {
    email: string = ""
    password2: string = ""
    readonly valid: RegisterUserIsValid

    constructor() {
        super()
        this.valid = new RegisterUserIsValid()
    }

    public get isValid(): boolean {
        this.valid.validateUsername(this.username)
        this.valid.validateEmail(this.email)
        this.valid.validatePasswordPair(this.password, this.password2)
        return this.valid.isValid
    }

}

class User {
    constructor(
        public _id: string,
        public username: string,
        public canCreateTests: boolean,
        public isSuperuser: boolean,
        public firstName: string,
        public surname: string,
        public lastName: string,
        public email?: string,
        public registrationDate?: string,
    ) {}
}

class UserTokens {
    constructor(
        public accessToken: string | null = null,
        public refreshToken: string | null = null
    ) {}
}

function createNewUser(data: any): User {
    return new User(data._id, data.username, data.canCreateTests, data.isSuperuser,
        data.firstName, data.surname, data.lastName, data.email, data.registrationDate)
}

class ChangePassword {
    constructor(
        public password1: string = "",
        public password2: string = ""
    ) {}

    public get valid() {
        return this.password1 === this.password2 && this.password1.length >= 8
    }
}

export {User, LoginUser, RegisterUser, ChangePassword, createNewUser, UserTokens}
