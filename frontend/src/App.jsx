import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { Route, Router, Routes } from 'react-router'
import Login from './components/Login'
import SalleList from './components/SalleList'
import ReservationForm from './components/ReservationForm'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
     
        <div className="min-h-screen bg-gray-100">
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/salles" element={<SalleList />} />
            <Route path="/reserve" element={<ReservationForm />} />
          </Routes>
        </div>
    
    </>
  )
}

export default App
