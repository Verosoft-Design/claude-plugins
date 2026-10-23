---
type: llm
---

The run was told not to post anything, so judge the comment it drafts and where it says the comment goes. Placeholders for upload URLs, links or the preview are fine: nothing has been uploaded yet.

PASS if all of these hold:
- The reply drafts a G5 Merge lifecycle comment and says it goes on the issue as a new top-level comment, not as a reply in the "This thread is for an agent session" thread.
- The drafted comment itself shows both screenshots as images (markdown image syntax), Before and After.
- The images come from uploading the files to Linear first (prepare_attachment_upload, a PUT, create_attachment_from_upload, then each upload's assetUrl).
- The comment refers to PR #1520, gives the test result (failed before the fix, passes after), mentions @gloria.chen for the merge, and ends with a status line waiting on G5.

FAIL if the comment is meant for the agent-session thread, or the screenshots are only in the PR description, only attached to the issue, or only linked rather than shown as images in the comment.
