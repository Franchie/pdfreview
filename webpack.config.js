const path = require('path');

var config = {
    devServer: {
        contentBase: path.resolve(__dirname),
        historyApiFallback: true,
        watchContentBase: true,
    },
    entry: {
        "index": './ui_src/index.tsx'
    },
    output: {
        filename: '[name].js',
        sourceMapFilename: "[name].js.map",
        path: path.resolve(__dirname, 'build'),
        publicPath: '/build/',
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
                test: /\.css$/i,
                use: 'css-loader'
            },
            {
                test: /\.(woff|woff2|eot|ttf|svg)$/,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]'
                }
            },
            {
                enforce: "pre",
                test: /\.js$/,
                loader: "source-map-loader"
            }
        ],
    }
};


module.exports = (env, argv) => {

    if (argv.mode === 'development') {
        config.devtool = 'eval-source-map';
    }

    else if (argv.mode === 'production') {
        config.devtool = 'source-map';
    }

    else {
        console.error("Could not find a suitable deployment mode");
    }

    return config;
};

