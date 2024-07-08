import React, {useState} from 'react';

function CreateSheet({ handleFinish }) {

    const [sheetName, setSheetName] = useState('New Sheet')

    const handleFinishClick = async () => {
        const formData = new FormData();
        formData.append('sheetName', sheetName);
        try {
            await fetch("http://localhost:5000/create_sheet", {
              method: 'POST',
              body: formData,
            }).then(res=> {
              console.log(res)
            })
          } catch (error) {
            console.error('Error:', error);
          }
        handleFinish()
    }

    return (
        <div>
            <h1>Create a new Sheet</h1>
            <button onClick={handleFinishClick}>Finish</button>
            <input type="text" defaultValue="New Sheet" placeholder='New Sheet' onChange={(e) => setSheetName(e.target.value)}></input>
        </div>
    )

}

export default CreateSheet;