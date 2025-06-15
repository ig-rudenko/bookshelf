import {validateEmail, validatePassword, validateTwoPasswords, validateUsername} from "@/validators.ts";

class LoginUserIsValid {
    username: boolean = true
    usernameError: string = ""
    password: boolean = true
    passwordError: string = ""

    validateUsername(value: string): void {
        this.usernameError = validateUsername(value);
        this.username = this.usernameError.length == 0;
    }

    validatePassword(value: string): void {
        this.passwordError = validatePassword(value)
        this.password = this.passwordError.length == 0;
    }

    get isValid(): boolean {
        return this.username && this.password;
    }

}

class RegisterUserIsValid extends LoginUserIsValid {
    email: boolean = true
    emailError: string = ""

    validateEmail(value: string): void {
        this.emailError = validateEmail(value)
        this.email = this.emailError.length == 0;
    }

    validatePasswordPair(pass1: string, pass2: string) {
        this.validatePassword(pass1)
        this.passwordError = validateTwoPasswords(pass1, pass2);
        this.password = this.passwordError.length == 0;
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
    recaptchaToken: string = ""
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
        public id: string,
        public username: string,
        public isSuperuser: boolean,
        public isStaff: boolean,
        public firstName?: string,
        public lastName?: string,
        public email?: string,
        public dateJoin?: string,
    ) {
    }
}

class UserTokens {
    constructor(
        public accessToken: string | null = null,
        public refreshToken: string | null = null
    ) {
    }
}

function createNewUser(data: any): User {
    return new User(data.id, data.username, data.isSuperuser, data.isStaff,
        data.firstName, data.lastName, data.email, data.dateJoin)
}

class ChangePassword {
    constructor(
        public password1: string = "",
        public password2: string = ""
    ) {
    }

    public get valid() {
        return this.password1 === this.password2 && this.password1.length >= 8
    }
}


function getUserAvatar(username: string): string {
    if (username) {
        return 'https://ui-avatars.com/api/?size=32&name=' + username + '&font-size=0.33&background=random&rounded=true'
    }
    return ""
}

export {User, LoginUser, RegisterUser, ChangePassword, createNewUser, UserTokens, getUserAvatar}
