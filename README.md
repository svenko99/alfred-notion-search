# <img src="images/notionxalfred.png" width="64"> Notion Search Workflow for Alfred

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![macOS](https://svgshare.com/i/ZjP.svg)](https://svgshare.com/i/ZjP.svg)

## 🤔 What is it?

- This Alfred workflow allows you to search for pages in your Notion workspace.
- It requires a Notion integration (API key).
- The workflow it quite fast.

## Installation

1. Install [⤓ Notion Search Workflow](https://github.com/svenko99/alfred-notion/releases/download/v1.1.0/notion_search.alfredworkflow) in the repo. You will be asked to put `Notion API key (of the integration)`. Follow steps in `2.` to get the API key.

2. Follow this [instructions](https://www.notion.so/help/create-integrations-with-the-notion-api#create-an-internal-integration) to create an internal integration and put the `Internal Integration Token` into the `Notion API key (of the integration)` which you will find in the `Configure Workflow`. There you will also find a checkbox if you wish that links of the pages are opened in the browser or in the Notion app.
  
3. Then open the Notion page that you want to be searchable and click on the three dots in the upper right corner.  
Select `Add Connection` and choose the integration you just created. *(You don't have to do this for every page as the pages within the page inherit the connection, so do this just for the main pages that appear on the left side of Notion.)*

4. You are good to go. 😃

## Usage

- In Alfred type `ns` and the page that you are searching for e.i. `ns programming` or `ns life`.
- If you hit enter on the outputed page it will open either in browser or in Notion app.
  ![screenshot](images/screenshot.png)

## To-do

- [ ] Convert emoji or a custom made icon of a page to image so it can be used as an icon (now they are in title).
- [ ] Add offline version, so the workflow will be even faster. The workflow will store the data of all pages to JSON file.
  - [ ] Add update functionally to offline version (JSON file will be updated with latest pages of your Notion workspace whenever you wish).
