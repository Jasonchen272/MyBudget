import React, {useState} from 'react';

function CreateSheet({ handleFinish }) {

    const [sheetName, setSheetName] = useState('New Sheet')
    const [isCreating, setIsCreating] = useState(false)
    const [createError, setCreateError] = useState(false)

    const handleFinishClick = async () => {
        setIsCreating(true)

        const formData = new FormData();
        formData.append('sheetName', sheetName);
        try {
            await fetch("http://localhost:5000/create_sheet", {
              method: 'POST',
              body: formData,
            })
          } catch (error) {
            console.log(error);
            
          } finally {
            if (!createError) {
              handleFinish()
            }
          }
    }

    return (
        <div>
            <h1>Create a new Sheet</h1>
            <input type="text" defaultValue="New Sheet" placeholder='New Sheet' onChange={(e) => setSheetName(e.target.value)}></input>
            <button onClick={handleFinishClick}>Finish</button>
            <div style={{display: isCreating ? "block" : "none"}}>Creating Spreadsheet...</div>
        </div>
    )

}

export default CreateSheet;