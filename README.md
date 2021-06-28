# Simple Twitter Backend

## Introduction
A simple Twitter backend using Django.

## Development environment setup
### Setup Vagrant
1. Virtual Box, Ubuntu 18
2. Install MySQL 8 noninteractively
3. Install and update pip
4. Add Django
5. Create a database named *twitter*.

## Development
### Accounts APIs
1. APIs
* login_status
* login
* signup
2. Tests

### Tweets APIs
1. Create a Tweet model (user, content, created_at), index on user+created_at
2. APIs
* list(GET)
* create(POST)

### Friendships APIs
1. Create a Friendship model (from_user, to_user, created_at) index on from_user+created_at, to_user+created_at.
2. APIs
* followers/followings(GET)
* follow/unfollow(POST)

### Newsfeeds APIs
1. Create a Newsfeed model (user, tweet, created_at) index on user+created_at
2. APIs
* newsfeeds(GET)
3. Add fanout logic in tweets creation API
