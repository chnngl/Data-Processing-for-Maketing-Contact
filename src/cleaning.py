import html
import re
import pandas as pd

PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "hotmail.com",
    "outlook.com",
    "icloud.com",
}

INVALID_NAME_VALUES = {
    "",
    "-",
    "n/a",
    "na",
    "null",
    "none",
}

def inspect_data(df: pd.DataFrame) -> None:
    print("---SHAPE---")
    print(df.shape)
    print()

    print("---COLUMN TYPE---")
    print(df.dtypes)
    print()

    print("---MISSING VALUE---")
    print(df.isna().sum())
    print()

    print("---SAMPLE ROW---")
    print(df.head(10).to_string(index=False))
    print()

def normalize_whitespace(value: str) -> str:
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value

def clean_name(raw_name: object) -> str:
    if pd.isna(raw_name):
        return ""
    name = html.unescape(str(raw_name))
    name = normalize_whitespace(name)

    #remove common prefixes like Dr.
    name = re.sub(r"^(dr|mr|mrs|ms)\.?\s+", "", name, flags=re.IGNORECASE)
    lowered = name.lower()
    if lowered in INVALID_NAME_VALUES:
        return ""
    #remove linkedin ad or non-person rows
    if "linkedin ads" in lowered or "sponsored" in lowered:
        return ""
    return name.title()

def extract_title(headline: object) -> str:
    if pd.isna(headline):
        return ""
    text = html.unescape(str(headline))
    text = normalize_whitespace(text)
    
    #keep first chunk when headline has |
    text = text.split("|")[0].strip()
    #remove company suffix like "Head of Marketing at Accenture"
    text = re.sub(r"\s+at\s+.+$", "", text, flags=re.IGNORECASE)
    #remove extra info after dash
    text = re.sub(r"\s+-\s+[A-Za-z0-9&.,' /]+$", "", text)
    #remove pronouns
    text = re.sub(r"\s*\((?:she/her|he/him|they/them|she/they|he/they)\)\s*", " ", text, flags=re.IGNORECASE
)
    return normalize_whitespace(text)

def standardize_company_name(company_name: object) -> str:
    if pd.isna(company_name):
        return ""
    company = html.unescape(str(company_name))
    company = normalize_whitespace(company).title()
    replacements = {
        "Google Ireland": "Google",
        "Meta Ireland": "Meta",
        "Oracle Ireland": "Oracle",
        "Sap Ireland": "SAP",
        "Sap": "SAP",
        "Linkedin": "LinkedIn",
        "Linkedin Ireland": "LinkedIn",
    }
    return replacements.get(company, company)

def infer_company_from_headline(headline: object) -> str:
    if pd.isna(headline):
        return ""
    text = html.unescape(str(headline))
    text = normalize_whitespace(text)
    #case like "VP of Marketing at LinkedIn"
    match = re.search(r"\bat\s+(.+)$", text, flags=re.IGNORECASE)
    if match:
        company = match.group(1).strip()
        company = re.sub(r"\s*\|.*$", "", company)
        company = re.sub(r"\s*-\s*.*$", "", company)
        return normalize_whitespace(company)
    return ""

def clean_url(profile_url: object) -> str:
    if pd.isna(profile_url):
        return ""
    url = normalize_whitespace(str(profile_url))
    if not url:
        return ""
    if url.startswith("linkedin.com/"):
        url = "https://" + url
    if not url.startswith("https://linkedin.com/in/"):
        return ""
    return url

def clean_email(email: object) -> str:
    if pd.isna(email):
        return ""
    value = normalize_whitespace(str(email)).lower()

    #reject phone numbers or invalid values
    email_pattern = r"^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$"
    if not re.fullmatch(email_pattern, value):
        return ""
    domain = value.split("@")[-1]
    #remove personal email
    if domain in PERSONAL_EMAIL_DOMAINS:
        return ""
    return value

def remove_irrelevant_rows(df: pd.DataFrame) -> pd.DataFrame:
    irrelevant_keywords = [
        r"\bsoftware engineer\b",
        r"\bchief financial officer\b",
        r"\bchief technology officer\b",
        r"\bchief executive officer\b",
        r"\bcfo\b",
        r"\bcto\b",
        r"\bceo\b",
        r"\btalent acquisition\b",
        r"\brecruiter\b",
        r"\bhr business partner\b",
        r"\bsales director\b",
        r"\baccount executive\b",
    ]

    titles = df["job_title"].fillna("").str.lower().str.strip()

    mask = ~titles.apply(
        lambda title: any(re.search(pattern, title) for pattern in irrelevant_keywords)
    )
    return df[mask].copy()

def deduplicate_profiles(df: pd.DataFrame) -> pd.DataFrame:
    deduped = df.copy()
    deduped["scraped_at"] = pd.to_datetime(deduped["scraped_at"], errors="coerce")

    #remove duplicate linkedin url as it points to same person
    with_url = deduped[deduped["linkedin_url"] != ""].copy()
    with_url = with_url.sort_values("scraped_at")
    with_url = with_url.drop_duplicates(subset=["linkedin_url"], keep="last")

    #check contact and company name for rows without usable linkedin url
    without_url = deduped[deduped["linkedin_url"] == ""].copy()
    without_url = without_url.sort_values("scraped_at")
    without_url = without_url.drop_duplicates(
        subset=["contact_name", "company_name"],
        keep="last",
    )
    combined = pd.concat([with_url, without_url], ignore_index=True)
    combined = combined.sort_values(["source_row_id"]).reset_index(drop=True)
    return combined


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["source_row_id"] = cleaned.index

    cleaned["contact_name"] = cleaned["raw_name"].apply(clean_name)
    cleaned["job_title"] = cleaned["headline"].apply(extract_title)
    
    cleaned["company_name"] = cleaned["company_name"].apply(standardize_company_name)
    missing_company_mask = cleaned["company_name"] == ""
    cleaned.loc[missing_company_mask, "company_name"] = (
    cleaned.loc[missing_company_mask, "headline"].apply(infer_company_from_headline))

    cleaned["email"] = cleaned["email"].apply(clean_email)
    cleaned["linkedin_url"] = cleaned["profile_url"].apply(clean_url)

    #remove rows missing the key identity fields
    cleaned = cleaned[
        (cleaned["contact_name"] != "") &
        (cleaned["job_title"] != "") 
    ].copy()
  
    cleaned = remove_irrelevant_rows(cleaned)
    cleaned = deduplicate_profiles(cleaned)

    #keep original raw order to check erased examples
    cleaned = cleaned.sort_values("source_row_id").reset_index(drop=True)

    cleaned = cleaned[
        ["contact_name", "job_title", "company_name", "linkedin_url", "email"]
    ].copy()
    return cleaned