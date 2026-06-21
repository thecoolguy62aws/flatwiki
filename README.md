# FlatWiki

## About

FlatWiki is a lightweight wiki engine. A FlatWiki is not your traditional wiki: it doesn't use any databases nor docker and is easy to set up on any machine with Python and pip. Simply pip install it, use the wizard to create a config file, and fire up the server! Then, you'll have a full wiki where you can log in to the administrator portal to modify, add, and delete pages to serve documents, instructions, or anything else to users.

## Installation and Usage

### Installation

1. Install via pip. Common commands are: `pip install flatwiki`, `pip3 install flatwiki`, `pipx install flatwiki`.
2. Navigate to a directory you would like to run flatwiki in.
3. Run `flatwiki config` and answer the prompts.
4. Run `flatwiki create-user` and add a administrator for you to log in as.
5. Run `flatwiki` to start the server!

### Usage

While the server is running, the root directory is public and users can browse the pages that admins created. By clicking `Admin Login` below the page names, you can see the admin portal. Log in with authorized credentials and then you will be greeted with a intuitive dashboard where you can create, edit, and delete pages.