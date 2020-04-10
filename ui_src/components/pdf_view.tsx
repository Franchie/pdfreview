/*
 * This component displays a pdf file along with annotations and callbacks
 * based on specific user actions.
 */

import React, { Component } from "react";
import { getDocument, PDFJS } from 'pdfjs-dist/webpack';

import 'typeface-roboto';



interface PdfViewProps {
    PdfURL: string;
};

interface PdfViewState {
};




export class PdfView extends React.Component<PdfViewProps, PdfViewState> {

    constructor(props: PdfViewProps) {
        super(props);
        this.state = {
        };
        //  - url: what is the url for the pdf file
        //  - cMapUrl / cMapPacked: where the cMaps are located
        //  - disableAutoFetch / disableStream / disableRange: this avoids making use of Ranged requests,
        //    which is not supported by ServiceWorkers used in offline mode
        let pdfOptions = {
            url: props.PdfURL,
            cMapUrl: 'cmaps/',
            cMapPacked: true,
            disableAutoFetch: true,
            disableStream: true,
            disableRange: true
        };
        getDocument(pdfOptions).promise.then(console.log);
    }

    render() {
        return (<div>Test div</div>
        );
    }
}

