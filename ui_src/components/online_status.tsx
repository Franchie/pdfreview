/*
 * This component displays an indication as to the offline/offline status
 * of the user.
 */

import React, { Component } from "react";

import { Avatar, Tooltip, CircularProgress } from "@material-ui/core";
import { CheckCircleTwoTone, AirplanemodeActive, AirplanemodeInactive, WarningOutlined } from "@material-ui/icons";

import 'typeface-roboto';


export enum OnlineStates {
    Online,
    OfflineAvailable,
    OfflineUnavailable,
    Problem,
    Syncing
};


export interface OnlineStatusState {
    onlineState: OnlineStates;
};


export class OnlineStatus extends React.Component<OnlineStatusState> {

    displayStateMessage(state: OnlineStates): string {
        switch(state) {
            case OnlineStates.Online:             return "Online";
            case OnlineStates.OfflineAvailable:   return "Offline, but storing your data for when the connection resumes";
            case OnlineStates.OfflineUnavailable: return "Offline, and not able to process requests";
            case OnlineStates.Problem:            return "There was a problem synchronising offline data";
            case OnlineStates.Syncing:            return "Synchronising offline data back to the server";
        }
    }

    displayStateIcon(state: OnlineStates) {
        let good_style: React.CSSProperties = { color: 'limegreen' };
        let bad_style: React.CSSProperties  = { color: 'orangered' };

        switch(state) {
            case OnlineStates.Online:             return <CheckCircleTwoTone style={good_style} />;
            case OnlineStates.OfflineAvailable:   return <AirplanemodeActive style={good_style} />;
            case OnlineStates.OfflineUnavailable: return <AirplanemodeInactive style={bad_style} />;
            case OnlineStates.Problem:            return <WarningOutlined style={bad_style} />;
            case OnlineStates.Syncing:            return <CircularProgress variant="indeterminate" disableShrink
                size={16} thickness={4} style={good_style}/>
        }
    }

    render() {
        return (
            <Tooltip title={ this.displayStateMessage(this.props.onlineState) }>
                { this.displayStateIcon(this.props.onlineState) }
            </Tooltip>
        );
    }
}

