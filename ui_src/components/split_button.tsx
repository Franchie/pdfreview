/*
 * Defines a split-button (button + dropdown for more options)
 * Properties are an array of choices, each one defining:
 *  - text: text to be displayed
 *  - callback: function(void) to call when this item is clicked
 *  - link: sets this up as a link to the url specified. If a callback is also provided,
 *      this will take precedence.
 */

import React, { Component } from 'react';
import { Grid, Button, ButtonGroup, ClickAwayListener, Grow, Paper, Popover, MenuItem, MenuList, Link } from "@material-ui/core";
import { ArrowDropDown } from "@material-ui/icons";



interface SpliButtonCallback {
    () : void;
};

interface SplitButtonChoices {
    text: string;
    callback?: SpliButtonCallback;
    link?: string;
};

export interface SplitButtonProps {
    Choices: Array<SplitButtonChoices>;
    className?: string;
};

interface SplitButtonState {
    open: boolean;
    anchor: HTMLElement | null;
};


export class SplitButton extends React.Component<SplitButtonProps, SplitButtonState> {

    constructor(props: SplitButtonProps) {
        super(props);
        this.state = {
            open: false,
            anchor: null
        };
    }

    handleClick = (event: React.MouseEvent<HTMLElement, MouseEvent>, index: number) => {
        let choice = this.props.Choices[index];
        if(choice.link && choice.callback) event.preventDefault();
        if(choice.callback) choice.callback();
        this.handleClose();
        return (!!choice.link);
    };

    handleToggle = (event: React.MouseEvent<HTMLElement, MouseEvent>) => {
        this.setState({
            open: !this.state.open,
            anchor: event.currentTarget
        });
    };

    handleClose = () => {
        this.setState({
            open: false,
            anchor: null
        });
    };

    render() {
        let { Choices, ...other } = this.props;

        function renderChoice(choice: SplitButtonChoices) {
            if (choice.link) {
                return (
                    <Link href={ choice.link } target="_blank">
                        { choice.text }
                    </Link>
                );
            } else {
                return (<span>{ choice.text }</span>);
            }
        }

        return (<>
            <ButtonGroup size="small" {...other} style={ this.state.open ? { visibility: "visible"} : {}}>
                <Button onClick={ (event) => this.handleClick(event, 0) }>
                    { renderChoice(Choices[0]) }
                </Button>
                <Button onClick={this.handleToggle}>
                    <ArrowDropDown />
                </Button>
            </ButtonGroup>
            <Popover anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'center',
            }} transformOrigin={{
                vertical: 'top',
                horizontal: 'center',
            }} open={this.state.open} onClose={this.handleClose} anchorEl={this.state.anchor}>
                <MenuList>
                    {Choices.map((choice, index) => (
                        <MenuItem key={index} selected={index === 0} onClick={event => this.handleClick(event, index)}>
                            { renderChoice(choice) }
                        </MenuItem>
                    ))}
                </MenuList>
            </Popover>
        </>);
    }
}

