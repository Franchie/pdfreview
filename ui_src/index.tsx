import React, { Component } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, useLocation, RouteComponentProps } from "react-router-dom";

import { AppBar, Container, CssBaseline, Toolbar, IconButton, Typography, Button } from "@material-ui/core";
import { Menu } from "@material-ui/icons";

import 'typeface-roboto';
import * as QueryParams from "./query_params";


// Main app interface. This is essentially a Router that selects between
// Browser and Editor mode, based on the presence of a 'review=<review id>'
// query parameter.
function App() {
    return (
        <Router>
            <CssBaseline />
            <Route component={AppViewSelector} />
        </Router>
    );
};


class AppViewSelector extends React.Component<RouteComponentProps> {

    // Determine whether there are any query parameters (eg: open review in editor)
    getURLParam(name: string): string | null {
        let query = new URLSearchParams(this.props.location.search);
        return query.get(name)
    }

    render() {
        let reviewID = this.getURLParam(QueryParams.review);

        // Top bar indicating possible actions
        const appbar = (
            <AppBar position="static">
                <Toolbar>
                    { reviewID ? (
                        <IconButton edge="start" color="inherit" aria-label="menu">
                            <Menu />
                        </IconButton>
                    ) : "" }
                    <Typography variant="h6" >
                        PDFReview
                    </Typography>
                    <Button color="inherit">Login</Button>
                </Toolbar>
            </AppBar>
        );

        // Main application context
        let view = (reviewID ? (
            <Typography>
                The review editor is not yet implemented
            </Typography>
        ) : (
            <Typography>
                The review list is not yet implemented
            </Typography>
        ));

        return (<>
            { appbar }
            { view }
        </>);
    }
}


/*
 * Application start
 * Register application after DOM loads.
 */
document.addEventListener('DOMContentLoaded', (event) => {
    ReactDOM.render(<App />, document.getElementById('root'));
});
