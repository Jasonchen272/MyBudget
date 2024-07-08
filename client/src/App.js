import React, {useState} from 'react'
import ImportFiles from './ImportFiles'
import CreateSheet from './CreateSheet'

function App() {
  const [currentPage, setCurrentPage] = useState('createPage')

  
  return (
    <div>
      <h1>MyBudget</h1>
      {currentPage === 'createPage' ? <CreateSheet handleFinish={ () => setCurrentPage('ImportPage')}/> : <ImportFiles />}
</div>

  )
}

export default App