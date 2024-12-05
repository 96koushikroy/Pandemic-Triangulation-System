import React from 'react';
import LoginPage from './components/Login/Login';
import { Routes, Route, BrowserRouter } from "react-router-dom";
import FourOhFour from './components/404/FourOhFour';
import HomePage from './components/Home/Home';


function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
            {/* <Route path="/" element={<HomePage />}> */}
            <Route index element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="*" element={<FourOhFour />} />
            {/* </Route> */}
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
