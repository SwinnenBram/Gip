import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// Haal token op uit localStorage en stel headers in
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Functie om de huidige ingelogde gebruiker op te halen
export const getCurrentUser = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user`, { headers: getAuthHeaders() });
    return response.data;
  } catch (error) {
    console.error('Fout bij ophalen van gebruiker:', error);
    return null;
  }
};

// Uitlogfunctie
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};
