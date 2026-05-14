# 2025 Annual Report Tracking Plan

## Purpose

Track which A-share firms have disclosed 2025 annual reports and which firms remain undisclosed before the 2026-04-30 statutory deadline.

The immediate use is to decide whether 2025 annual reports can support a near-term pilot for GAI-assisted financial-disclosure writing.

## Status Date

Current tracking date: 2026-04-28.

Important deadline: China A-share 2025 annual reports are generally expected to be disclosed by 2026-04-30.

## Source Priority

1. CNINFO annual-report announcements.
2. Shanghai Stock Exchange and Shenzhen Stock Exchange scheduled-disclosure pages.
3. Eastmoney / iFinD / Wind-style annual-report calendars as secondary cross-checks.

## Required Fields

For each company:

- stock code;
- company name;
- exchange;
- scheduled annual-report disclosure date;
- whether the 2025 annual report has been disclosed;
- actual disclosure date if available;
- delay or correction announcement if available;
- source URL and retrieval date.

## Working Definitions

`Disclosed`: a 2025 annual report announcement is available through CNINFO or the relevant exchange.

`Not yet disclosed`: no 2025 annual report announcement is available as of the retrieval date, and the scheduled date is after the retrieval date or the firm has announced a delay.

`Needs manual verification`: source pages conflict or only a preview/calendar entry is available.

## Pilot Output

The first tracking output should be:

```text
results/annual_report_2025_pending_20260428.csv
docs/annual_report_2025_pending_20260428.md
```

The CSV should be source-oriented, not cleaned beyond recognition. If source coverage is incomplete, keep a `source_status` column rather than silently filling values.

