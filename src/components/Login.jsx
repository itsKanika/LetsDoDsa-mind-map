import './Login.css';

const Login = ({ setIsLoggedIn }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    // dummy login action
    setIsLoggedIn(true);
  };

  return (
    <div className="wrapper">
      <div className="image-container">
        <img src="/images/loginImg-3.jpg" alt="Background" />
        <div className="login-box">
          <center><h1>Login</h1></center>
          <form id="login-form" onSubmit={handleSubmit}>
            <div className="cls">
              <input type="text" id="username" name="username" placeholder="Username" required />
              <i className="fas fa-user"></i>
            </div>
            <div className="cls">
              <input type="email" id="email" name="email" placeholder="Email" required />
              <i className="fas fa-envelope"></i>
            </div>
            <div className="cls">
              <input type="password" id="password" name="password" placeholder="Password" required />
              <i className="fas fa-lock"></i>
            </div>
            <input type="submit" value="Login" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
