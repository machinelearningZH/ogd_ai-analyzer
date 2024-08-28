# 🦄 OGD Auto AI Analyzer
**Almost automatically analyze the quality of a DCAT metadata catalog. With a little help from ✨ AI...**

![GitHub License](https://img.shields.io/github/license/machinelearningzh/ogd_ai-analyzer)
[![PyPI - Python](https://img.shields.io/badge/python-v3.9+-blue.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer)
[![GitHub Stars](https://img.shields.io/github/stars/machinelearningZH/ogd_ai-analyzer.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/machinelearningZH/ogd_ai-analyzer.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer/issues)
[![GitHub Issues](https://img.shields.io/github/issues-pr/machinelearningZH/ogd_ai-analyzer.svg)](https://img.shields.io/github/issues-pr/machinelearningZH/ogd_ai-analyzer) 
[![Current Version](https://img.shields.io/badge/version-0.1-green.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer)
<a href="https://github.com/astral-sh/ruff"><img alt="linting - Ruff" class="off-glb" loading="lazy" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>

<details>
<summary>Contents</summary>

- [Usage](#usage)
- [What does the code do?](#what-does-the-code-do)
- [What exactly do we check?](#what-exactly-do-we-check)
- [Why check metadata?](#background-why-check-metadata)
    - [How to fix this?](#how-to-fix-this)
- [Project team](#project-team)
- [Feedback and contributing](#feedback-and-contributing)

</details>

## Usage
- Create a [Conda](https://conda.io/projects/conda/en/latest/index.html) environment: `conda create -n analyzer python=3.9`
- Activate environment: `conda activate analyzer`
- Clone this repo.
- Change into the project directory.
- Install packages: `pip install -r requirements.txt`
- You need to **create an [OpenAI API key](https://platform.openai.com) to use the LLM-based assessments**. Create an `.env` file and input your API keys like so:
```
    OPENAI_API_KEY=sk-...
```
- Open the notebooks in your favorite IDE and run the code.
- Check the results (in folder `_results`) and fix issues in your metadata.

> [!Note]
> The notebook is set up as a [Quarto](https://quarto.org/) file. You don't need to use Quarto. You can simply run the notebook as is and look at the results. However, we encourage you to try it out with Quarto. The results will be much more shareable, e.g. to a non technical audience, that doesn't want or need to see code. Simply [install Quarto](https://quarto.org/docs/get-started/), add [an extension to your IDE](https://quarto.org/docs/tools/vscode.html) and convert the notebook to an HTML oder PDF file.

## What does the code do?
We carry out **a thorough metadata analysis and quality check using our own [OGD metadata catalog of the Canton of Zurich](https://www.zh.ch/de/politik-staat/statistik-daten/datenkatalog.html#/) as an example**.

This project is based on two simple ideas:

- We **treat the metadata catalog as a regular dataset and do a structured and detailed exploratory data analysis (EDA).** 
- We **use an LLM to analyze the content of titles and descriptions to discover semantic deficits and nonsensical entries that are hard to catch otherwise**.

We set up the code to perform most of the checks automatically. It should be easy to adapt this notebook to other data catalogues that conform to the [DCAT-AP CH standard](https://www.dcat-ap.ch/).

The two notebooks produces the following outputs:

- a **HTML report** detailing all issues that were found
- an **Excelfile with all major issues** categorized and sortable
- another **Excelfile with a qualitative assessment of title and description of each dataset** created by an LLM

> [!Important]
> At the risk of stating the obvious: By using the code parts for the LLM-based analysis **you send data to a third-party provider** namely [OpenAI](https://platform.openai.com/docs/overview). **Therefore only use non-sensitive data.** Again, stating the obvious: **LLMs make errors.** They regularly hallucinate, make things up, and get things wrong. They often do so in subtle, non-obvious ways, that may be hard to detect. This app is **meant to be used as an assistive system that makes suggestions.** It **only yields a draft of an analyis, that you always should double-check.** 

## What exactly do we check?
We focus on the following points:

- Conformity to the DCAT standard
- Missing values
- Hidden nulls (e.g., "", "null", "none", "nichts")
- Empty lists and dictionaries
- Duplicates
- Text issues in titles and descriptions, such as unstripped text, line breaks, escape sequences, control characters, and unnecessary whitespace
- Abbreviations that might erode understandability or make search unneccesarily hard
- Titles copied verbatim to descriptions or ressource descriptions, adding no new information
- Overall **semantic quality of titles and descriptions (✨ powered by an LLM)**
- Date issues, such as non-parsable dates and start dates that come after end dates
- Issues in individual properties
- Offline or invalid landing pages and distributions
- and many more...

These checks encompass the metadata at both the dataset and distribution levels.

With the second notebook you get an **in depth analysis of each datasets title and description**. We prompt an ✨ LLM to assess if title and description explain clearly and in detail:

- what the dataset is about («Dateninhalt»), 
- how the data was collected («Entstehungszusammenhang»), 
- how the data quality is («Datenqualität»), 
- what the spacial aggregation is («Räumlicher Bezug»), 
- and how the data can be linked to other data («Verknüpfungsmöglichkeiten»). 

You also get a score for each dataset from 1 (least informative) to 5 (most informative). The scoring is as follows:

- 1 point - No information about this criterion.
- 2 points - Few information, much is missing.
- 3 points - Average information, some information is available, some is missing.
- 4 points - Good information, most information is available.
- 5 points - Excellent information, everything is very clear, complete, and detailed.

## Background: Why check metadata?
Metadata is essential for data users. Only with an understanding of context, methodology, content, and quality can they fully utilize the data. Creating good metadata requires time and effort. Unfortunately, not all metadata meets sufficient quality standards. We observe issues both in our catalog and others, such as [opendata.swiss](https://opendata.swiss/de).

Swiss OGD offerings follow the [DCAT-AP CH standard](https://www.dcat-ap.ch/), the «Swiss Application Profile for Data Portals and Catalogues». While DCAT is beneficial and widely adopted, it can be easily «hacked».

- It is simple **to create a dataset entry that conforms to the standard, but lacks meaningful content**. You can do this for example by simply inputting empty strings, lists or dictionaries for mandatory fields, or by just inputting a single nonsensical element like one character or number. 
- You can also **«misuse» the standard by copying the title into the description field**, adding no additional information. 

These are real issues. If you look at OGD catalogues you'll easily find many of these examples and also quite a few datasets that perfectly adhere to the standard but are completely broken.

> [!Note]
> These problems are not the «fault» of DCAT. The standard is a sincere recommendation, but it cannot ensure that every entry is meaningful. This responsibility lies with us as data stewards and publishers.

### How to fix this?
As of the time of writing, our own OGD lists ~800 datasets and opendata.swiss ~12,000 datasets. Manually checking each dataset for metadata quality issues is unrealistic. One way to improve this is by developing **automatic procedures to programmatically check and highlight metadata issues**. This project suggests a template and hopefully some fresh ideas to achieve this.

## Project team
This is a project of [Team Data of the Statistical Office of the Canton of Zurich](https://www.zh.ch/de/direktion-der-justiz-und-des-innern/statistisches-amt/data.html). Responsible: Laure Stadler and Patrick Arnecke. Many thanks go to **Corinna Grobe** and our former colleague **Adrian Rupp**. Merci! ❤️

## Feedback and contributing
We would love to hear from you. Please share your feedback and let us know how you use the code. You can [write an email](mailto:datashop@statistik.zh.ch) or share your ideas by opening an issue or a pull requests.

Please note that we use [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting with default settings.
