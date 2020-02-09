/*
 * This is the main view for the review creation/list view.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";

import { AppBar, Toolbar, Container, Typography } from "@material-ui/core";

import 'typeface-roboto';
import { FilteredReviewCollection, ReviewDetails } from "./components/filtered_review_collection";
import { OnlineStatus, OnlineStates } from "./components/online_status";



interface ReviewViewState {
    reviews: Array<ReviewDetails>;
};

export interface ReviewViewProps {
    onlineState: OnlineStates;
};


export class ReviewView extends React.Component<ReviewViewProps, ReviewViewState> {

    constructor(props: ReviewViewProps) {
        super(props);
        this.state = {
            reviews: [
                { author: 'A A', name: 'Review 1', id: 'dkjfghskhjdf1'},
                { author: 'B G', name: 'A fancy review I like', id: 'dkjfghskhjdf2'},
                { author: 'Heai Jrwe', name: 'Numero tres', id: 'dkjfghskhjdf3'},
                { author: 'Henri duChamp', name: 'En Français?', id: 'dkjfghskhjdf4'},
                { author: 'Hf kr', name: 'This is not a review', id: 'dkjfghskhjdf5'},
                { author: 'Caor sltf', name: 'dfkgjhla lktjhsd glsdfg', id: 'dkjfghskhjdf6'},
                { author: 'John Bekg', name: 'This is some long text that really goes on waaaaaaay too long for its own good', id: 'dkjfghskhjdf7'},
                { author: 'Bulwer fsldf', name: 'Manual instriuction', id: 'dkjfghskhjdf'}
            ]
        };
    }


    render() {
        // Top bar indicating possible actions
        const appbar = (
            <AppBar position="sticky">
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
                <FilteredReviewCollection
                    Title="Recent reviews"
                    Collection={ this.state.reviews}
                    Filter={ (a) => (Math.random() > 0.5) /* Example filter */} />
                <FilteredReviewCollection
                    Title="Open reviews"
                    Collection={ this.state.reviews}
                    EmptyMessage="No reviews" />
                <FilteredReviewCollection
                    Title="Closed reviews"
                    Collection={ this.state.reviews}
                    Filter={ (a) => (Math.random() > 0.5) /* Example filter */} />
            </Container>
        </>);
    }
}

