import React, { Component } from "react";
import ReactDOM from "react-dom";

console.log("Started v2")

class MyComponent extends React.Component {
    render() {
        return (
            <div>This is a test</div>
        );
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    ReactDOM.render(<MyComponent/>, document.getElementById('root'));
});
