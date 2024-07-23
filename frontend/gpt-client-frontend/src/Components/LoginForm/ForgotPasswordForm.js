import React from 'react';
import { Link } from 'react-router-dom';
import './LoginForm.css';

function ForgotPasswordForm() {
    return (
        <div className="wrapper">
            <div className="form-box forgot-password">
                <form>
                    <h1>Forgot Password</h1>
                    <h2>Enter your email to reset your password</h2>
                    <div className="input-box">
                        <input type="email" placeholder="Email" required />
                        <span className="icon"><i className="fas fa-envelope"></i></span>
                    </div>
                    <button type="submit">Send Reset Link</button>
                    <div className="register-link">
                        <p>Remembered your password? <Link to="/login">Login</Link></p>
                    </div>
                    <div className="footer">
                        <p>&copy; Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ForgotPasswordForm;