document.getElementById("firstButton").addEventListener("click", () => {
    document.getElementById("register").style.display="none";
    document.getElementById("login").style.display="block";
}, false);

document.getElementById("secondButton").addEventListener("click", () => {
    document.getElementById("login").style.display="none";
    document.getElementById("register").style.display="block";
}, false);


const { createApp } = Vue

const login = createApp({
    data() {
        return {
            imgCode: '/account/api/captcha/',
            username: '',
            password: '',
            captcha: '',
            message: ''
        }
    },
    methods: {
        login() {
            $.ajax('/account/api/login/', {
                type: 'POST',
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                data: JSON.stringify({
                    'username': this.username,
                    'password': this.password,
                    'captcha': this.captcha
                }),
                dataType: 'json',
                success: function (data, textStatus, jqXHR) {
                    if (data.code === 10000) {
                        location.href = '/shopper/'
                    } else {
                        this.message = data.message,
                        this.imgCode += '?',
                        this.captcha = ''
                    }
                }.bind(this),
                error: function (jqXHR, textStatus, errorThrown) {
                        this.message = ''
                }.bind(this)
            })
        }
    }
})

login.mount('#login')

const register = createApp({
    data() {
        return {
            imgCode: '/account/api/captcha/',
            username: '',
            password_1: '',
            password_2: '',
            agreement: '',
            captcha: '',
            message: ''
        }
    },
    methods: {
        register() {
            axios({
                url: '/account/api/register/',
                method: 'post',
                headers: {
                    'content-type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                data: JSON.stringify({
                    username: this.username,
                    password_1: this.password_1,
                    password_2: this.password_2,
                    agreement: this.agreement,
                    captcha: this.captcha
                }),
                responseType: 'json'
            })
            .then(response => {
                if (response.data.code === 10000) {
                    location.href = '/account/'
                } else {
                    this.message = response.data.message,
                    this.imgCode += '?',
                    this.captcha = ''
                }
            })
        }
    }
})

register.mount('#register')
