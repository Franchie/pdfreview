/*
 * This component manages the creation of a new review.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";

import { Fab, Tooltip } from "@material-ui/core";
import { Add } from "@material-ui/icons";

import 'typeface-roboto';



interface CreateReviewState {
};

export interface CreateReviewProps {
};


export class CreateReview extends React.Component<CreateReviewProps, CreateReviewState> {

    constructor(props: CreateReviewProps) {
        super(props);
        this.state = {
        };
    }

    browseForFile() {
        console.log("Browsing for a file to upload")
    }

    render() {
        return (
            <Tooltip title="Click here to start a new review">
                <Fab color="secondary" onClick={this.browseForFile} style={{ position: 'fixed', right: 20, bottom: 20}}>
                    <Add />
                </Fab>
            </Tooltip>
        );
    }
}

