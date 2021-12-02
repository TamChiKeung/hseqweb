FROM node:12.16

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package.json .
COPY package-*.json .

RUN npm install -g @angular/cli@9.0.7
RUN npm install
# If you are building your code for production
RUN npm ci --only=production

# Bundle app source
COPY . .

EXPOSE 8080
EXPOSE 443
CMD ng build && ng serve --port 8080 --host 0.0.0.0 --proxy-config proxy.conf.json --disable-host-check
