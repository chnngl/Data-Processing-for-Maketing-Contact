# Marketing Contacts Data Cleaning

## Overview

This project processes a raw CSV of LinkedIn-style marketing contact data and produces a cleaned contact list of the primary marketing decision-maker at each company.

## Final Output
The final output file is at:

`data/output/marketing_contacts_clean.csv`

Another output file under the same path is
`cleaned_data_without_classification.csv`. It provides a preview of the cleaned data before selecting the senior marketing roles for the company.

## Common Issues Found During Data Inspection:
- Name contains extra whitespace, titles such as “Dr.”, inconsistent case formatting (all capitalization or mixed), and some invalid entries like "N/A", "-", or LinkedIn ad content.
- Headline contains HTML entity like  &amp, special character like "-" or "|" that combines job title, company name, pronouns, etc. Assumptions made include the first section before | is usually the title, and if the headline is like "VP of Marketing at LinkedIn", assume the word after "at" is the company name.
- Some rows represented irrelevant roles, such as software engineering or sales positions.
- Company names were sometimes missing or inconsistently formatted, like Google or Google Ireland.
- LinkedIn profile URLs included missing values and incomplete links.
- Email data included missing values, phone numbers found in the email field, and personal email addresses.
- Duplicate entries appeared across multiple scrape dates. If the contact name and LinkedIn URL are the same across entries, only the latest scraped one is kept. When the URL is invalid, and contact and company names are both same across entries, assume they refer to the same person, and only the latest scraped data is kept.

## Classification and Ranking Logic
A pattern-based classification approach was used, where the titles were treated as relevant when they combined:
- a seniority rank such as Chief, CMO, VP, Head, Director, or Lead
- a marketing-related function such as Marketing, Brand, Growth

Exact title matching was applied at first, but it's rigid and less result was generated. 

The contacts are ranked by seniority in the following order:

- Chief Marketing Officer / CMO
- VP of Marketing
- Head-level marketing roles
- Director-level marketing roles
- Lead-level marketing roles

If there are multiple senior role contacts from the same company, the one with the highest rank will be kept. If there was a tie, the most recent scraped_at value was used.

## Limitations
Some company names are missing, and a few can be inferred from headlines, but that doesn't apply to all cases. Although it worked for this file, maybe it shouldn't be treated as certain.

Some of the rule-based filtering remains rigid, especially when excluding clearly irrelevant roles based on headline text, as it can be sensitive to title wording. In the meantime, role classification has a similar problem as marketing titles vary across companies, and equivalent senior roles may be expressed in different ways.

With more time, I would make the exclusion and classification logic more robust.
