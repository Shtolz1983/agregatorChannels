# agregatorChannels

TODO describe 

### Used technologies
* Python;
* Telethon;
* Docker and Docker Compose (containerization);
* Redis (persistent storage for some ongoing game data);

## Installation
Make directories for bot's data:

Grab `.env.dot` file, rename it to `.env`, open and fill the necessary data.

Change `redis.conf` values for your preference.

Run script
`.make_volumes.sh`
Directories wil be created in `${HOME}/${VOLUMES_DIR}` path

Finally, start your bot with `docker-compose up -d` command.
