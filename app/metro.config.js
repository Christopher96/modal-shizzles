// Learn more https://docs.expo.io/guides/customizing-metro
const { getDefaultConfig } = require("expo/metro-config");

/** @type {import('expo/metro-config').MetroConfig} */
const config = getDefaultConfig(__dirname);
config.server.rewriteRequestUrl = (url) => {
  console.log(url);
  return url;
};

module.exports = config;
