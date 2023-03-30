# 📝 Notion workflow for Alfred

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)

## 🤔 What is it?

- This Alfred workflow allows you to search for pages in your Notion workspace.
- It requires a Notion integration (API key).
- The workflow it quite fast.

## Installation

- Follow this [instructions](https://www.notion.so/help/create-integrations-with-the-notion-api#create-an-internal-integration) to create an internal integration and put the `Internal Integration Token` into the `Notion API key (of the integration)` which you will find in the `Configure Workflow...`

  - There you will also find a checkbox if you wish that links of the pages are opened in the browser or in the Notion app.

- The last thing to do is to install [⤓ Notion Search Workflow](https://github.com/svenko99/alfred-notion/raw/main/notion_search.alfredworkflow) in the repo.

## Usage

- In Alfred type `ns` and the page that you are searching for e.i. `ns programming` or `ns life`.
- If you hit enter on the outputed page it will open either in browser or in Notion app.

## To-do

- [ ] Convert emoji or a custom made icon of a page to image so it can be used as an icon (now they are in title)
