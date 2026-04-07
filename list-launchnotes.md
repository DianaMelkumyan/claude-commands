---
name: list-launchnotes
description: List all LaunchNotes assigned to me that are ready for review.
---

# List Launch Notes

Query the LaunchNotes Announcements Tracker and show all items assigned to me with status "Ready for Review".

## Context

- LaunchNotes DB: `https://www.notion.so/thanxwiki/30ca84ed4024803caf34c2739b77ad1a?v=30ca84ed4024803a948b000c7e10aa7e`
- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`

## Instructions

1. Fetch the LaunchNotes database using the Notion fetch tool with the URL above.
2. Query the database view to get all entries.
3. Filter for items where:
   - **PM/Reviewer** includes me (user ID above)
   - **Status** is "Ready for Review"
4. Display a table with columns: Feature name, Status, Publish Date, and Notion URL.
5. If items exist, offer options:
   - "Want me to **review all of these in parallel**? (`/review-all-launchnotes`)"
   - "Or pick a number to review just one."
6. If no items found, say: "No launch notes assigned to you are ready for review right now."
