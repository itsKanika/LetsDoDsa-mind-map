// components/MainLayout.jsx
import React, { useEffect } from "react";
import Navbar from "./Navbar/Navbar";
import { Outlet, useLocation } from "react-router-dom";
import Footer from "./Footer/Footer";
import ThemeToggle from "./ThemeToggle";
import Chatbot from "./Chatbot/Chatbot";

const MainLayout = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    // More reliable scroll methods
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "smooth", // or 'auto'
    });

    // Alternative method
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
  }, [pathname]);

  return (
    <div className="min-h-screen overflow-x-hidden">
      <Navbar />
      <Outlet />
      <ThemeToggle />
      <Chatbot />
      <Footer />
    </div>
  );
};

export default MainLayout;
