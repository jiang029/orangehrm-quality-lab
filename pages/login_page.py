class LoginPage:
    """只封装登录页已经重复出现的定位和操作。"""

    def __init__(self, page, base_url):
        self.page = page
        self.url = f"{base_url}/web/index.php/auth/login"
        self.username_input = page.get_by_placeholder("Username")
        self.password_input = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.invalid_credentials_message = page.get_by_text(
            "Invalid credentials",
            exact=True,
        )
        self.dashboard_heading = page.get_by_role("heading", name="Dashboard")

    def open(self):
        self.page.goto(self.url)

    def login(self, username, password):
        # Locator.fill/click 自带 actionability 自动等待，调用方无需固定 sleep。
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
