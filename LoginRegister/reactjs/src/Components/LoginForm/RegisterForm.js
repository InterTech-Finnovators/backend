import React from 'react';
import { Link } from 'react-router-dom';
import './LoginForm.css';

function RegisterForm() {
    return (
        <div className="wrapper">
            <div className="form-box register">
                <form>
                    <h1>Create Account</h1>
                    <div className="input-box">
                        <input type="text" placeholder="Username" required />
                        <span className="icon"><i className="fas fa-user"></i></span>
                    </div>
                    <div className="input-box">
                        <input type="email" placeholder="Email" required />
                        <span className="icon"><i className="fas fa-envelope"></i></span>
                    </div>
                    <div className="input-box">
                        <input type="password" placeholder="Password" required />
                        <span className="icon"><i className="fas fa-lock"></i></span>
                    </div>
                    <button type="submit">Register</button>
                    <div className="register-link">
                        <p>Already have an account? <Link to="/login">Login</Link></p>
                    </div>
                    <div className="footer">
                        <p>&copy; Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default RegisterForm;