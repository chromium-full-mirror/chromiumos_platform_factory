// Copyright 2018 The ChromiumOS Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

const path = require('path');
const tsconfigPathsWebpackPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = {
  devtool: 'source-map',
  entry: ['./src/index'],
  module: {
    rules: [{
      test: /\.tsx?$/,
      use: [{
        loader: 'ts-loader',
        options: {
          transpileOnly: true,
          experimentalWatchApi: true,
        },
      }],
    }],
  },
  name: 'main',
  output: {
    filename: 'app.js',
    path: path.resolve(__dirname, 'build'),
    pathinfo: false,
    publicPath: '/static/',
  },
  optimization: {
    emitOnErrors: false,
  },
  performance: {hints: false},
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
    plugins: [new tsconfigPathsWebpackPlugin()],
    fallback: {buffer: require.resolve("buffer/")},
  },
  devServer: {
    allowedHosts: 'all',
    host: '0.0.0.0',
    port: 8080,
    static: {
      directory: path.join(__dirname, 'build'),
      publicPath: '/',
    },
  },
};
