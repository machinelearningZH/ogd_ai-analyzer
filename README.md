# 🦄 OGD Auto AI Analyzer

**Almost automatically analyze the quality of a DCAT metadata catalog with a little help from ✨ AI.**

![GitHub License](https://img.shields.io/github/license/machinelearningzh/ogd_ai-analyzer)
[![PyPI - Python](https://img.shields.io/badge/python-v3.10+-blue.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer)
[![GitHub Stars](https://img.shields.io/github/stars/machinelearningZH/ogd_ai-analyzer.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/machinelearningZH/ogd_ai-analyzer.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer/issues)
[![GitHub Issues](https://img.shields.io/github/issues-pr/machinelearningZH/ogd_ai-analyzer.svg)](https://img.shields.io/github/issues-pr/machinelearningZH/ogd_ai-analyzer)
[![Current Version](https://img.shields.io/badge/version-0.2-green.svg)](https://github.com/machinelearningZH/ogd_ai-analyzer)
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
- [Disclaimer](#disclaimer)

</details>

## Usage

```bash
# Clone the repository
git clone https://github.com/statistikZH/ogd_ai-analyzer.git
cd ogd_ai-analyzer

# Install uv and dependencies
pip3 install uv
uv venv
source .venv/bin/activate
uv sync
```

- You need to **create an [OpenRouter API key](https://openrouter.ai/keys) to use the LLM-based assessments**. Create an `.env` file and input your API key like so:

```
    OPENROUTER_API_KEY=sk-or-v1-...
```

- Open the notebooks in your favorite IDE and run the code.
- Check the results (in folder `_results`) and fix issues in your metadata.

> [!Note]
> The notebooks are set up as [Quarto](https://quarto.org/) files. You don't need to use Quarto. You can simply run the notebooks as is and look at the results. However, we encourage you to try it out with Quarto. The results will be much more shareable, e.g., to a non-technical audience that doesn't want or need to see code. Simply [install Quarto](https://quarto.org/docs/get-started/), add [an extension to your IDE](https://quarto.org/docs/tools/vscode.html), and convert the notebooks to HTML or PDF files. You can also render the EDA notebook directly from the command line:

```bash
quarto render 01_mdv_quality_checks.ipynb
```

## What does the code do?

We perform **a thorough metadata analysis and quality check using the [OGD metadata catalog of the Canton of Zurich](https://www.zh.ch/de/politik-staat/statistik-daten/datenkatalog.html#/) as an example**.

This project:

- **Treats the metadata catalog as a regular dataset and performs a structured, detailed exploratory data analysis (EDA)**
- **Uses an LLM to analyze titles and descriptions to discover semantic deficits and nonsensical entries that are hard to catch otherwise**

We set up the code to perform most of the checks automatically. It should be easy to adapt these notebooks to other data catalogs that conform to the [DCAT-AP CH standard](https://www.dcat-ap.ch/).

The two notebooks produce the following outputs:

- a **HTML report** detailing all issues that were found
- an **Excel file with all major issues** categorized and sortable
- another **Excel file with a qualitative assessment of the title and description of each dataset** created by an LLM

> [!Important]
> Use of the LLM-based analysis code results in **data being sent to third-party model providers through [OpenRouter](https://openrouter.ai)**, which brokers requests to multiple LLM services. **Do not submit sensitive or confidential data.**

> [!Important] 
> **LLMs make errors.** This app **provides suggestions only** and **yields a draft analysis that you should always double-check.**

## What exactly do we check?

- Conformity to the DCAT standard
- Missing values
- Hidden nulls (e.g., "", "null", "none", "nichts")
- Empty lists and dictionaries
- Duplicates
- Text issues in titles and descriptions, such as unstripped text, line breaks, escape sequences, control characters, and unnecessary whitespace
- Abbreviations that might erode clarity or make search unnecessarily hard
- Titles copied verbatim to descriptions or resource descriptions, adding no new information
- Overall **semantic quality of titles and descriptions (✨ powered by an LLM)**
- Date issues, such as non-parsable dates and start dates that come after end dates
- Issues in individual properties
- Offline or invalid landing pages and distributions
- and many more...

These checks cover metadata at both dataset and distribution levels.

The second notebook provides an **in-depth analysis of each dataset's title and description**. An ✨ LLM assesses whether the title and description clearly explain:

- what the dataset is about («Dateninhalt»),
- how the data was collected («Entstehungszusammenhang»),
- how the data quality is («Datenqualität»),
- what the spatial aggregation is («Räumlicher Bezug»),
- and how the data can be linked to other data («Verknüpfungsmöglichkeiten»).

Each dataset receives a score from 1 (least informative) to 5 (most informative):

- 1 point - No information about this criterion.
- 2 points - Little information, much is missing.
- 3 points - Average information, some information is available, some is missing.
- 4 points - Good information, most information is available.
- 5 points - Excellent information, everything is very clear, complete, and detailed.

## Background: Why check metadata?

Metadata is essential for data users to fully understand context, methodology, content, and quality. Creating good metadata requires time and effort, yet not all metadata meets sufficient quality standards. We observe issues in our catalog and others, such as [opendata.swiss](https://opendata.swiss/de).

Swiss OGD offerings follow the [DCAT-AP CH standard](https://www.dcat-ap.ch/). While widely adopted, it can be easily «hacked».

- **Dataset entries can conform to the standard but lack meaningful content** by inputting empty strings, lists or dictionaries for mandatory fields, or by inputting a single nonsensical element like one character or number
- **The standard can be «misused» by copying the title into the description field**, adding no additional information

OGD catalogues contain many such examples, plus datasets that perfectly adhere to the standard but are completely broken.

> [!Note]
> These problems are not the «fault» of DCAT. The standard is a sincere recommendation, but it cannot ensure that every entry is meaningful. This responsibility lies with us as data stewards and publishers.

### How to fix this?

Our OGD catalog lists ~1,050 datasets and opendata.swiss lists ~14,000 datasets. Manually checking each dataset for metadata quality issues is unrealistic. We address this by developing **automatic procedures to programmatically check and highlight metadata issues**. This project provides a template and fresh ideas to achieve this.

## Project Team

**Laure Stadler**, **Chantal Amrhein**, **Patrick Arnecke** – [Statistisches Amt Zürich: Team Data](https://www.zh.ch/de/direktion-der-justiz-und-des-innern/statistisches-amt/data.html)

Many thanks also go to **Corinna Grobe** and our former colleague **Adrian Rupp**.

## Feedback and contributing

We would love to hear from you. Please share your feedback and let us know how you use the code. You can [write an email](mailto:datashop@statistik.zh.ch) or share your ideas by opening an issue or pull request.

Please note that we use [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting with default settings.

## Disclaimer

This software (the Software) incorporates models (Models) from OpenAI and others and has been developed according to and with the intent to be used under Swiss law. Please be aware that the EU Artificial Intelligence Act (EU AI Act) may, under certain circumstances, be applicable to your use of the Software. You are solely responsible for ensuring that your use of the Software as well as of the underlying Models complies with all applicable local, national and international laws and regulations. By using this Software, you acknowledge and agree (a) that it is your responsibility to assess which laws and regulations, in particular regarding the use of AI technologies, are applicable to your intended use and to comply therewith, and (b) that you will hold us harmless from any action, claims, liability or loss in respect of your use of the Software.
