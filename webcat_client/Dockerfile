# get node image
FROM node:18.15

# set working directory
# Application will be present in /workspace directory
WORKDIR /workspace

# copy all files except those in .dockerignore
COPY . .

# install dependencies
RUN npm install

# expose port 3000
EXPOSE 3000

# start application
CMD ["npm", "start"]

