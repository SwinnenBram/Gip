import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get("http://localhost:5000/api/user", {
          withCredentials: true,  // Zorg dat cookies worden meegestuurd
        });
        setUser(response.data);
      } catch (error) {
        setUser(null); // Gebruiker is niet ingelogd
      }
    };

    fetchUser();
  }, []);

  const logout = async () => {
    await axios.post("http://localhost:5000/api/logout", {}, { withCredentials: true });
    setUser(null);
  };

  return (
    <UserContext.Provider value={{ user, setUser, logout }}>
      {children}
    </UserContext.Provider>
  );
};
