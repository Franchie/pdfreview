/*
 * This component displays a (optionally filtered) list of review card
 */

import React, { Component } from "react";

import { Container, Paper, Typography } from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';

import { ReviewCard } from "./review_card";
import 'typeface-roboto';



export interface ReviewDetails {
    name: string;
    author: string;
    id: string;
};

interface ReviewFilterFunction {
    (review: ReviewDetails): boolean;
}

export interface FilteredReviewCollectionProps {
    Title: string;
    EmptyMessage?: string;
    Filter?: ReviewFilterFunction;
    Collection: Array<ReviewDetails>;
};


export function FilteredReviewCollection(props: FilteredReviewCollectionProps) {
    function filter(collection: Array<ReviewDetails>, filterFnc?: ReviewFilterFunction | null) {
        if(!filterFnc) return collection;
        return collection.filter(filterFnc);
    }

    const reviews = filter(props.Collection, props.Filter);

    return (
        <div style={{
            display: (reviews.length == 0 && !props.EmptyMessage) ? 'none' : 'block',
            marginTop: 50
        }}>
            <Typography variant="h4">
                { props.Title }
            </Typography>
            <Paper style={{padding: 20, margin: 10}}>
                <Container>
                    {reviews.map((review, index) => (
                        <ReviewCard key={review.id} Title={review.name} Author={review.author} ReviewID={review.id} />
                    ))}
                    <div style={{ display: (reviews.length > 0) ? 'none' : 'block' }}>
                        { props.EmptyMessage }
                    </div>
                </Container>
            </Paper>
        </div>
    );
}

