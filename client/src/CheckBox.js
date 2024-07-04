import React from 'react'

export default function checkBox({switchBool, text}) {
    function handleSwitch() {
        switchBool()
    }
    return (
        <div style={{display: "flex"}}>
            <input type="checkbox" onChange={handleSwitch} />
            <p>{text}</p>
          </div>
    )
}

