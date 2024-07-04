import React, {useState} from 'react'
import CheckBox from './CheckBox'
import NumberPicker from './NumberPicker'

function App() {
  const [file, setFile] = useState()
  const [month, setMonth] = useState('january')
  const [bank, setBank] = useState('wells_fargo')
  const [fileTypeError, setFileTypeError] = useState(false)
  const [otherFormat, setOtherFormat] = useState({'skip': false, 'date': 0, 'description': 1, 'amount': 2, 'isCredit': false})

  const months = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
  ]

  function handleChange(event) {
    setFile(event.target.files[0])
    setFileTypeError(false)
  }

  function checkValidFormat() {
    const dateColumn = otherFormat.date;
    const descriptionColumn = otherFormat.description
    const amountColumn = otherFormat.amount;

    if (Number.isNaN(dateColumn) || Number.isNaN(descriptionColumn) || Number.isNaN(amountColumn)) {return false}

    return !((dateColumn === descriptionColumn) || (amountColumn === descriptionColumn) || (amountColumn === dateColumn))
  }
  
  const handleSubmit = async (event) =>{
    event.preventDefault()


    if (!file) {
      setFileTypeError(true)
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fileName', file.name);
    formData.append('month', month);
    formData.append('bank', bank);
    if (bank === "other") {
      if (!checkValidFormat()) { console.log("invalid format"); return; }
      formData.append('otherFormat', JSON.stringify(otherFormat));
    }

    try {
      console.log("in try")
      await fetch("http://localhost:5000/files", {
        method: 'POST',
        body: formData,
      }).then(res=> {
        console.log(res)
      })
    } catch (error) {
      console.error('Error:', error);
    }
  }

  
  return (
    <div>
      <h1>MyBudget</h1>
      <div>Upload a CSV file and select bank and month</div>
    <form onSubmit={handleSubmit}>
      <input type="file" onChange={handleChange}/>
      <select onChange={(e) => setMonth(e.target.value)}>
        {months.map(month => {
          return  (
            <option value={month.charAt(0).toLowerCase() + month.slice(1)} key={month}>{month}</option>
          )        
        })}
      </select>  
      <select onChange={(e) => setBank(e.target.value)}>
        <option value="wells_fargo">Wells Fargo</option>
        <option value="discover">Discover</option>
        <option value="capital_one">Capital One</option>
        <option value="other">Other</option>
      </select>  
      <button type="submit">Upload</button>
    </form>
    <div style={{ display: bank === "other" ? "block" : "none" }}> 
      Please input the format of your file
      <CheckBox 
          switchBool={() => setOtherFormat(prevFormat => ({
            ...prevFormat, 
            skip: !prevFormat.skip
          }))}
          text = "Skip First Line?" />
        <CheckBox 
          switchBool={() => setOtherFormat(prevFormat => ({
            ...prevFormat, 
            isCredit: !prevFormat.isCredit
          }))}
          text = "is Credit?" />
      Count the columns starting from 0

      <div style={{display: "flex"}}>
      <NumberPicker 
      text="Date column"
      defaultValue={0}
      onChange={ (e) =>
        setOtherFormat(prevFormat => ({
         ...prevFormat, 
          date: parseInt(e.target.value)
        }))
        } />

    <NumberPicker 
      text="Description column"
      defaultValue={1}
      onChange={ (e) =>
        setOtherFormat(prevFormat => ({
         ...prevFormat, 
          description: parseInt(e.target.value)
        }))
        } />
        <NumberPicker 
      text="Date column"
      defaultValue={2}
      onChange={ (e) =>
        setOtherFormat(prevFormat => ({
         ...prevFormat, 
          amount: parseInt(e.target.value)
        }))
        } />        
      </div>
    </div>
    
    <div style={{ display: fileTypeError ? "block" : "none" }}>Wrong file type or name</div>
</div>

  )
}

export default App