// src/components/AdminLogin.js
import React, { useState } from 'react';
import axios from 'axios';

function AdminLogin({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/api/admin/login', {
                username,
                password
            });
            setMessage('Login succesvol! Je hebt toegang tot het admin dashboard.');
            onLogin(); // Informeer het bovenliggende component dat de admin is ingelogd
        } catch (error) {
            setMessage('Ongeldige gebruikersnaam of wachtwoord');
        }
    };

    return (
        <div>
            <h2>Admin Login</h2>
            <form onSubmit={handleLogin}>
                <div>
                    <label>Username:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <button type="submit">Login</button>
            </form>
            <p>{message}</p>
        </div>
    );
}

export default AdminLogin;
