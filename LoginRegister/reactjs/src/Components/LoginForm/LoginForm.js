import React from 'react';
import { Link } from 'react-router-dom';
import './LoginForm.css';

function LoginForm() {
    return (
        <div className="wrapper">
            <div className="form-box login">
                <form>
                    <h1>Welcome </h1>
                    <h2>Please sign in to your account </h2>
                    <div className="input-box">
                        <input type="text" placeholder="Username" />
                        <span className="icon"><i className="fas fa-user"></i></span>
                    </div>
                    <div className="input-box">
                        <input type="password" placeholder="Password" />
                        <span className="icon"><i className="fas fa-lock"></i></span>
                    </div>
                    <div className="remember-forgot">
                        <label>
                            <input type="checkbox" /> Remember me
                        </label>
                        <Link to="/forgot-password">Forgot password?</Link>
                    </div>
                    <button type="submit">Login</button>
                    <div className="register-link">
                        <p>Don't have an account? <Link to="/register">Register</Link></p>
                    </div>
                    <div className="footer">
                        <p>&copy; Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default LoginForm;