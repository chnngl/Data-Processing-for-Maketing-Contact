import re
import pandas as pd

def is_senior_marketing_role(job_title: str) -> bool:
    title = str(job_title).lower().strip()

    seniority_patterns = [
        r"\bchief\b",
        r"\bcmo\b",
        r"\bvp\b",
        r"\bhead\b",
        r"\bdirector\b",
        r"\blead\b",
    ]

    marketing_patterns = [
        r"\bmarketing\b",
        r"\bbrand\b",
        r"\bgrowth\b",
        r"\bmarketing operations\b",
    ]

    has_seniority = any(re.search(pattern, title) for pattern in seniority_patterns)
    has_marketing = any(re.search(pattern, title) for pattern in marketing_patterns)
    return has_seniority and has_marketing

def get_seniority_rank(job_title: str) -> int:
    title = str(job_title).lower().strip()

    if re.search(r"\bchief marketing officer\b", title) or re.fullmatch(r"cmo", title):
        return 1
    if re.search(r"\bvp\b", title):
        return 2
    if re.search(r"\bhead\b", title):
        return 3
    if re.search(r"\bdirector\b", title):
        return 4
    if re.search(r"\blead\b", title):
        return 5
    return 999

def select_best_contacts(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df[df["job_title"].apply(is_senior_marketing_role)].copy()

    filtered["scraped_at"] = pd.to_datetime(filtered["scraped_at"], errors="coerce")
    filtered["seniority_rank"] = filtered["job_title"].apply(get_seniority_rank)

    filtered = filtered.sort_values(
        by=["company_name", "seniority_rank", "scraped_at", "source_row_id"],
        ascending=[True, True, False, True],
    )
    best_per_company = filtered.drop_duplicates(subset=["company_name"], keep="first").copy()
    final_df = best_per_company[
        ["company_name", "contact_name", "job_title", "email", "linkedin_url"]
    ].reset_index(drop=True)

    return final_df