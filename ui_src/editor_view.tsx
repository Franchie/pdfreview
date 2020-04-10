/*
 * This is the main view for the review creation/list view.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";

import { AppBar, BottomNavigation, BottomNavigationAction, Toolbar, Container, Typography, Link } from "@material-ui/core";
import { LiveHelp, MenuBook, GitHub } from "@material-ui/icons";

import 'typeface-roboto';
import { FilteredReviewCollection, ReviewDetails } from "./components/filtered_review_collection";
import { CreateReview } from "./components/create_review";
import { PdfView } from "./components/pdf_view";
import { OnlineStatus, OnlineStates } from "./components/online_status";



interface EditorViewState {
};

export interface EditorViewProps {
    onlineState: OnlineStates;
};


export class EditorView extends React.Component<EditorViewProps, EditorViewState> {

    constructor(props: EditorViewProps) {
        super(props);
        this.state = {
        };
    }



    render() {
        // Top bar indicating possible actions
        const appbar = (
            <AppBar position="sticky" style={{backgroundColor: '#009fc1'}}>
                <Toolbar variant="dense">
                    <Typography variant="h6" >
                        PDFReview
                    </Typography>
                    <section style={{marginLeft: 'auto'}}>
                        <OnlineStatus onlineState={this.props.onlineState} />
                    </section>
                </Toolbar>
            </AppBar>
        );

        // Main view
        return (<>
            { appbar }
            <Container>
                <PdfView PdfURL="/pdfs/sample.pdf" />
            </Container>
        </>);
    }
}

