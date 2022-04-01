# agregatorChannels


A simple script that allows you to create a channel and subscribe other specialized channels to it. So order the subscriptions and read only those. channels you have created. You can subscribe to a channel by forwarding a message from it to the created channel. In order to unsubscribe from the channel, you just need to delete the recent message.

### Used technologies
* Python;
* Telethon;
* Docker and Docker Compose (containerization);
* Redis (persistent storage for some ongoing game data);

## Installation
Make directories for bot's data:

* Grab `.env.dot` file, rename it to `.env`, open and fill the necessary data.
* How to get information about the api id and hash is described here: https://telethon.readthedocs.io/en/latest/basic/signing-in.html
* To get the SESSION_STRING variable, run the login.py file

Change `redis.conf` values for your preference.

Run script
`.make_volumes.sh`
Directories wil be created in `${HOME}/${VOLUMES_DIR}` path

Finally, start your bot with `docker-compose up -d` command.
