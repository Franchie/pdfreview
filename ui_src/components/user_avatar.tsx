/*
 * This component displays a user's initials within a
 * circle, used to represent a given user.
 */

import React, { Component } from "react";

import { Avatar, Tooltip } from "@material-ui/core";
import { Menu } from "@material-ui/icons";

import { colorFromText } from '../util/color_from_text';
import 'typeface-roboto';



export enum UserAvatarSize {
    Small = 24,
    Medium = 32,
    Large = 48
};


export interface UserAvatarProps {
    name: string;
    color?: string;
    textColor?: string;
    size?: UserAvatarSize;
};


export class UserAvatar extends React.Component<UserAvatarProps, UserAvatarProps> {

    getInitials(name: string): string {
        let words = name.split(" ");
        let initials = words.map((s) => (s.charAt(0)));
        switch(initials.length) {
            case 0: return "?";
            case 1: return initials[0].toUpperCase();
            default: return (initials[0] + initials[initials.length - 1]).toUpperCase();
        }
    }

    render() {
        let colorPair = colorFromText(this.props.name)
        let size = this.props.size || UserAvatarSize.Medium;

        let style: React.CSSProperties = {
            height: size,
            width: size,
            fontSize: size / 2,
            backgroundColor: this.props.color || colorPair.color,
            color: this.props.textColor || colorPair.text
        };

        return (
            <Tooltip title={ this.props.name }>
                <Avatar style={ style }>{ this.getInitials(this.props.name) }</Avatar>
            </Tooltip>
        );
    }
}

