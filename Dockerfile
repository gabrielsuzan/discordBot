#FROM node:12.5.3
#FROM node:12.5.3 as common-build-stage
FROM node:latest
# Create the bot's directory
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY package.json /usr/src/bot
RUN npm install

COPY . /usr/src/bot

# Start the bot.
CMD ["node", "index.js","config.json"]
