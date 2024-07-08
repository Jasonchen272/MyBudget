import React from 'react';

function NumberPicker({text, defaultValue, onChange}) {
    function handleChange(e) {
        onChange(e);
    }

    return (
        <div style={{display: "flex"}}>
        <p>{text}</p>
        <input type="number"  
        defaultValue={defaultValue}
        placeholder={defaultValue}
        onChange={ (e) =>handleChange(e) }
        />
        </div>
    );
}

export default NumberPicker;