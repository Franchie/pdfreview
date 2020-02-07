const path = require('path');

module.exports = {
    devtool: 'eval-source-map',
    devServer: {
        contentBase: path.resolve(__dirname),
        historyApiFallback: true,
        watchContentBase: true,
    },
    entry: {
        "review-list": './ui_src/review-list.ts'
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'js'),
        publicPath: '/js/',
    },
    resolve: {
        extensions: ['.ts', '.tsx', '.js'],
    },
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                enforce: "pre",
                test: /\.js$/,
                loader: "source-map-loader"
            }
        ],
    }
};

