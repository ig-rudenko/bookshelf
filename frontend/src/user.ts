

class LoginUserIsValid {
    username: boolean = true
    password: boolean = true
}

class RegisterUserIsValid extends LoginUserIsValid {
    email: boolean = true
}



class LoginUser {
    username: string
    password: string
    readonly valid: LoginUserIsValid

    constructor(username: string = "", password: string = "") {
        this.username = username
        this.password = password
        this.valid = new LoginUserIsValid()
    }

    public get isValid(): boolean {
      this.valid.username = this.username.length > 2
      this.valid.password = this.password.length > 8
      return this.valid.username && this.valid.password
    }

}

class RegisterUser extends LoginUser {
    email: string
    readonly valid: RegisterUserIsValid

    constructor(username: string = "", email: string = "", password: string = "") {
        super(username, password)
        this.email = email
        this.valid = new RegisterUserIsValid()
    }

    public get isValid(): boolean {
      this.valid.username = this.username.length > 2
      this.valid.email = this.email.length > 0 && this.email.indexOf("@") > 0
      this.valid.password = this.password.length > 8
      return this.valid.username && this.valid.email && this.valid.password
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
