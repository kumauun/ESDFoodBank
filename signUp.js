const API_URL = 'http://127.0.0.1:5000/api';

const SignUp = {
    template: '#signup-template',
    data() {
        return {
            username: '',
            password: ''
        };
    },
    methods: {
        async submitForm() {
            try {
                const response = await fetch(`${API_URL}/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password
                    })
                });

                if (!response.ok) {
                    throw new Error('Error during sign up');
                }

                alert('Account created. You can now sign in.');
                this.$emit('navigate', 'signin');
            } catch (error) {
                alert(error.message);
            }
        }
    }
};

const SignIn = {
    template: '#signin-template',
    data() {
        return {
            username: '',
            password: ''
        };
    },
    methods: {
        async submitForm() {
            try {
					const response = await fetch(`${API_URL}/signin`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password
                    }),
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error('Invalid credentials');
                }

                const data = await response.json();
                this.$emit('login', data.username);
                this.$emit('navigate', 'dashboard');
            } catch (error) {
                alert(error.message);
            }
        }
    }
};

const Dashboard = {
    template: '#dashboard-template',
    props: ['username'],
    methods: {
        async signout() {
            try {
                const response = await fetch(`${API_URL}/signout`, {
                    method: 'POST',
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error('Error during sign out');
                }

                this.$emit('logout');
                this.$emit('navigate', 'signin');
            } catch (error) {
                alert(error.message);
            }
        }
    }
};

const app = new Vue({
    el: '#app',
    data: {
        currentComponent: 'signin',
        loggedIn: false,
        username: ''
    },
    components: {
        'sign-up': SignUp,
        'sign-in': SignIn,
        'dashboard': Dashboard
    },
    methods: {
        navigate(component) {
            this.currentComponent = component;
        },
        login(username) {
            this.loggedIn = true;
            this.username = username;
        },
        logout() {
            this.loggedIn = false;
            this.username = '';
        }
    }
});