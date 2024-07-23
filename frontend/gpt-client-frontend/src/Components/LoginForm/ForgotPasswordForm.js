import React from 'react';
import { Link } from 'react-router-dom';
import './LoginForm.css';

function ForgotPasswordForm() {
    return (
        <div className="wrapper">
            <div className="form-box forgot-password">
                <form>
                    <h1>Forgot Password</h1>
                    <h2>Enter your new password</h2>
                    <div className="input-box">
                        <input type="email" placeholder="Email" required />
                        <span className="icon"><i className="fas fa-envelope"></i></span>
                    </div>
                    <div className="input-box">
                        <input type="password" placeholder="New Password" required />
                        <span className="icon"><i className="fas fa-lock"></i></span>
                    </div>
                    <button type="submit">Set New Password</button>
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