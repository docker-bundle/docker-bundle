# Docker Bundle
### Docker-bundles manager, installer.
* Require [Docker](https://docs.docker.com/install/)
* Require [Docker-compose](https://pypi.org/project/docker-compose/) (pip3 install docker-compose)
* Automatically install, build running and publishing programs in docker.
*  Best choice For **Lazy**, **Silly** and **Impatient** Developer

## Installation
* Mac, Linux
	```
	curl -L https://docker-bundle.github.io/install.sh | bash
	```
	or  See [Docker-bundle-wrapper](https://github.com/docker-bundle/docker-bundle-wrapper)
* Windows  

	See [Docker-bundle-wrapper](https://github.com/docker-bundle/docker-bundle-wrapper)


## version 0.1.0

####  Usage

***

***Xiaoming*** is a lazy programmer, he want to build a rails project on his Macbook Pro

But he is too lazy to install  a complete set of development environment.

So he choose docker-bundle (**Very wise choice**). 

```
> curl -L https://docker-bundle.github.io/install.sh | bash
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   377  100   377    0     0    161      0  0:00:02  0:00:02 --:--:--   161
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 18248  100 18248    0     0   9780      0  0:00:01  0:00:01 --:--:--  9779

Manually put it into your .bashrc or .zshrc:
    export PATH=$HOME/.docker-bundle/bin:$PATH
```
He put `    export PATH=$HOME/.docker-bundle/bin:$PATH` in his .zshrc, check docker-bundle install   

```
>  . ~/.zshrc
>  docker-bundle

    Docker-bundle

Usage:
    docker-bundle [options] [COMMAND] [ARGS...]

Options:
    -h|--help
    -v|--version
    -e|--environment <ENV>                  Set environment variables to commands
       --check-upgrade                      Check self upgrade before action
       --upgrade                            Do self upgrade directly (without ask) if upgrade available

Commands:
    install                       Install bundle here
    search                        Search for bundle you want
    source                        Manage sources
```

and run docker-bundle search for rails bundle
```
>  docker-bundle search rails
NAME                                    Description
rails                                   Rails bundle
rails:pg-yarn                           Rails bundle for postgres and yarn
```
He create a empty folder and into it, choose  `rails:pg-yarn` (he like postgres and yarn) and install, 
```
>  mkdir bitcoin_rails
>  cd bitcoin_rails 
>  docker-bundle install rails:pg-yarn
   ...
Please input your project name [bitcoin_rails]:[Enter]

----------------------------------------------------------------------------------------------------
                         Rails on Docker

    ENV=development               [development(default), staging, production]    ( -e ENV=?)
----------------------------------------------------------------------------------------------------
Bundle Commands:
    rails:new                     Create new rails project here in docker
    rails:sync                    Install depends, Migrate db
    rails:seed                    Install depends, migrate db and run seed
    rails:c                       Rails console
    rails:build                   Build static assets (for staging/production environments)
    rails:db:drop                 Drop database (only available development/staging environments)
    env:init                      Initial Project Env Config
    run                           Run a command with a container
    exec                          Exec a command in container
    shell                         Open a Shell into container, if container not start, use `run bash`
    logs                          Show logs
    up                            Create && start server
    down                          Stop && remove  server
    start                         Start server
    stop                          Stop server
    restart                       Restart server
```
Docker-bundle installed a bundle of command for him.  
Follow the hint, he type
```
> docker-bundle rails:new
----------------------------------------------------------------------------------------------------
                         Rails on Docker

    ENV=development               [development(default), staging, production]    ( -e ENV=?)
----------------------------------------------------------------------------------------------------

Long long wait.....

Lot lot install....

=============================================================================================
            INSTALL FINISH
=============================================================================================

Now you will add this config (inside '++++') manually by default database connection config

Open `config/database.yml`:
------------------------------------------------------------------------------
default: &default
  ...
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  username: postgres
  password:
  host: <%= ENV.fetch('DATABASE_HOSTNAME', '127.0.0.1') %>
  port: 5432
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  ...
------------------------------------------------------------------------------
```
His rails project seem to be created. Docker-bundle hint him to configure database connection.   
Follow the hint, he copy 
```
  username: postgres
  password:
  host: <%= ENV.fetch('DATABASE_HOSTNAME', '127.0.0.1') %>
  port: 5432
```
and type `vim config/database.yml`, paste into `default: ` scope

Next,  docker-bundle will install all of depends and databases for him.   
He type:
```
> docker-bundle rails:seed

Long long wait.....

Lot lot install....

Yarn install...

Fetch gems...

Migration db...

Seed data...

......

Create databases `bitcoin_rails_development`
Create databases `bitcoin_rails_test`
```
Ummmmm, everything's ready...

```
>  docker-bundle up
```
Rails-on-docker is waiting for him on http://0.0.0.0:3000   

---

***XiaoHong*** is silly programmer. She can only work on Windows.  
She need learn Rails which seems hard to work on Windows.  
So she choose docker-bundle (**Have no choice**).   

Soon she found, the installation command
```
curl -L https://docker-bundle.github.io/install.sh | bash
```
seems not working on Windows.  

Finally she goes to [Docker-bundle-wrapper](https://github.com/docker-bundle/docker-bundle-wrapper), which could run docker-bundle wrapper in docker environment, can help her run docker-bundle on windows.   

Follow the `README.md` of   [Docker-bundle-wrapper](https://github.com/docker-bundle/docker-bundle-wrapper), she create a bat file  named as `docker-bundlew.bat` (with magic code inside) , which serve as `docker-bundle` command on windows.

 Put `docker-bundlew.bat` into `C:\User\Xiaohong\.docker-bundle\bin`   (or any else she like)

and add `docker-bundlew.bat` into `%PATH%`, open a new cmd she  type
```
C:\User\Xiaohong\> docker-bundle

Command not found...

C:\User\Xiaohong\> docker-bundlew

   ...
Docker image push....
   ...

    Docker-bundle

Usage:
    docker-bundle [options] [COMMAND] [ARGS...]

Options:
    -h|--help
    -v|--version
    -e|--environment <ENV>                  Set environment variables to commands
       --check-upgrade                      Check self upgrade before action
       --upgrade                            Do self upgrade directly (without ask) if upgrade available

Commands:
    install                       Install bundle here
    search                        Search for bundle you want
    source                        Manage sources
C:\User\Xiaohong\>
```
It's seems work!  Next she follow ***Xiaoming*** 's steps create and runing her first Rails project on Windows.

---
***XiaoHui*** is a arrogant programmer, he think docker-bundle is unnecessary for experienced programmer like him.

He create and install Rails project spend a week.(lol)
