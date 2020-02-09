import React, { Component } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, useLocation, RouteComponentProps } from "react-router-dom";

import { CssBaseline, Typography } from "@material-ui/core";

import 'typeface-roboto';
import * as QueryParams from "./query_params";
import { ReviewView } from "./review_view";
import { OnlineStatus, OnlineStates, OnlineStatusState } from "./components/online_status";



type GlobalState = OnlineStatusState /* & ... */;


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


class AppViewSelector extends React.Component<RouteComponentProps, GlobalState> {

    constructor(props: RouteComponentProps) {
        super(props);
        this.state = {
            onlineState: OnlineStates.OfflineUnavailable
        };
    }

    // Determine whether there are any query parameters (eg: open review in editor)
    getURLParam(name: string): string | null {
        let query = new URLSearchParams(this.props.location.search);
        return query.get(name)
    }

    render() {
        let reviewID = this.getURLParam(QueryParams.review);

        // Main application context
        let view = (reviewID ? (
            <Typography>
                The review editor is not yet implemented
            </Typography>
        ) : (
            <ReviewView onlineState={this.state.onlineState} />
        ));

        return view;
    }
}


/*
 * Application start
 * Register application after DOM loads.
 */
document.addEventListener('DOMContentLoaded', (event) => {
    ReactDOM.render(<App />, document.getElementById('root'));
});
