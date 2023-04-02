const API_URL = 'http://127.0.0.1:5006';

app.component('Navbar', {
  template: `
    <nav class="navbar navbar-expand-lg bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">Savood</a>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNavAltMarkup"
          aria-controls="navbarNavAltMarkup"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
          <div class="navbar-nav">
            <a class="nav-link disabled" aria-current="page">Home</a>
            <a class="nav-link" href="listing.html">Listing</a>
            <a class="nav-link" href="history.html">History</a>
            <a class="nav-link" href="currentdelivery.html">Current Delivery</a>
            <a class="nav-link" href="settings.html">Settings</a>
            <a class="nav-link" @click="logout" style="cursor: pointer;">Logout</a>
          </div>
        </div>
      </div>
    </nav>
  `,
  methods: {
    async logout() {
        try {
            const response = await fetch(`${API_URL}/logout`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('Error during logout');
            }

            const data = await response.json();

            this.message = data.message;
            this.userId = '';
            this.userType = '';
            this.userNameSession = '';
            const userType = localStorage.getItem('userType');
            if(userType == 'restaurant'){
              href_page = '../foodbankUI/signUp.html'
            } else if (userType == 'foodbank'){
              href_page = './signUp.html'
            } else if (userType == 'driver'){
              href_page = '../foodbankUI/signUp.html'
            }
            localStorage.removeItem('userId');
            localStorage.removeItem('userType');
            localStorage.removeItem('userNameSession');

            window.location.href = href_page;
        } catch (error) {
            this.message = error.message;
        }
    },
  },
});
