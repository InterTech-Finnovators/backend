import React from 'react';
import { Link } from 'react-router-dom';
import './LoginForm.css';

function RegisterForm() {
    return (
        <div className="wrapper">
            <div className="form-box register">
                <form action="">
                    <h1>Register</h1>
                    <div className="input-box">
                        <input type="text" placeholder="Username" required />
                        <i className='bx bxs-user'></i>
                    </div>
                    <div className="input-box">
                        <input type="email" placeholder="Email" required />
                        <i className='bx bxs-envelope'></i>
                    </div>
                    <div className="input-box">
                        <input type="password" placeholder="Password" required />
                        <i className='bx bxs-lock-alt'></i>
                    </div>
                    <button type="submit">Register</button>
                    <div className="login-link">
                        <p>Already have an account? <Link to="/login">Login</Link></p>
                    </div>
                    <div className="footer">
                        <p>© Finnovators. All rights reserved.</p>
                    </div>
                </form>
            </div>
        </div>
    );

}


export default RegisterForm;