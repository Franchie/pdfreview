/*
 * This component displays a card that allows a review to be opened or configured
 */

import React, { Component } from "react";

import { Card, CardContent, CardActions, Button, ButtonGroup, Typography, Link } from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';
import { Close } from "@material-ui/icons";

import * as QueryParams from "../query_params";
import { UserAvatar, UserAvatarProps, UserAvatarSize } from "./user_avatar";
import { SplitButton } from "./split_button";
import 'typeface-roboto';


export interface ReviewCardProps {
    Title: string;
    Author: string;
    ReviewID: string;
};


const useStyles = makeStyles({
    root: {
        width: 320,
        margin: 5,
        display: 'inline-block',
        '&:hover $actions': {
            visibility: 'visible'
        },
        backgroundColor: '#f5ffff'
    },
    container: {
        display: 'flex',
        alignItems: 'center',
        padding: 10
    },
    cardContent: {
        display: 'block',
        paddingLeft: 10
    },
    actions: {
        visibility: 'hidden'
    }
});


export function ReviewCard(props: ReviewCardProps) {
    const classes = useStyles();

    function reviewURL(reviewID: string): string {
        return ('?' + QueryParams.review + '=' + reviewID);
    }

    const buttonOptions = [
        { text: "Open", link: ('?' + QueryParams.review + '=' + props.ReviewID) },
        { text: "Rename" },
        { text: "Download archive" },
        { text: "Close" },
    ]

    return (
            <Card className={classes.root}>
                <div className={classes.container}>
                    <UserAvatar name={props.Author} size={UserAvatarSize.Large} />
                    <div className={classes.cardContent}>
                        <Typography variant="h6">{ props.Title }</Typography>
                        <SplitButton Choices={buttonOptions} className={classes.actions} />
                    </div>
                </div>
        </Card>
    );
}

