import './App.css'
import { Routes, Route } from 'react-router-dom'
import Layout from './component/Layout'
import Welcome from './component/Welcome'
import Chat from './component/Chat'

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Welcome />} />
          <Route path="/chat" element={<Chat />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
