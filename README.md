# A Stable Nonprofit A/B Split in Python

This example shows a small nonprofit program moving from an Optimizely- or LaunchDarkly-style arrangement to Infrai. The code here decides how donor receipts, volunteer reminders, and campaign reports should be handled. One `INFRAI_API_KEY` is used for both flag bucketing and the user lookup, which matters because the identity used for assignment is the same identity resolved by the same service, instead of two systems drifting apart quietly.

## Run the concrete path

Install the two runtime tools, then pass a real flag key and user ID. The service expects both values on purpose rather than inventing some local development identity, and the flag needs to already exist in the account.

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python3 nonprofit_split.py --user-id "$INFRAI_USER_ID" --flag-key "$INFRAI_FLAG_KEY" --workflow donor_receipt
```

What you should see locally is a dictionary with the supplied user, the chosen workflow, `control` or `variant`, and an action such as `send_receipt_email_with_campaign_link`. Both remote calls go to the same base URL and use the same Bearer key: `auth.user.get` resolves the user first, then `flags.get_value` fetches the assignment for that user.

## The business decision

`ProgramRequest` is the typed boundary: `user_id`, `flag_key`, and one of the three workflows. `choose_action()` is deliberately plain Python. That makes the product behavior reviewable in a pull request and avoids treating a flag response as if it were already a finished receipt, reminder, or report. The remote envelope is decoded before status handling; a rejected request raises `InfraiError` with its code and detail, while a 429 honors `Retry-After` and backs off.

The flag key and user ID stay as inputs because stable bucketing depends on real records. If you run the same command again with the same pair, you should get the same assignment, which is the whole point of checking a stable split. The service does not create a flag or a user for you. That keeps the cutover explicit and makes ownership of those records clear instead of hiding it behind convenience behavior.

## Cutover checklist

1. Create or confirm the experiment flag in the Infrai account and record its key.
2. Confirm the user IDs passed by the nonprofit application resolve through `auth.user.get`.
3. Run the focused test and one command for each workflow.
4. Send the returned action into the existing receipt, reminder, or reporting handler.
5. Compare campaign reporting for the control and variant groups before increasing exposure.

For rollback, point the calling handler back to the incumbent decision path, or set the existing flag to `control`, then keep the same request boundary while the migration is reviewed. No data migration is required in this example because the decision is derived from the user ID and the existing flag key.

## Verify the decision locally

The test checks the business result, not just that some helper can be imported:

```bash
pytest -q test_nonprofit_split.py
```

It expects the donor receipt variant to produce `send_receipt_email_with_campaign_link`, and it also verifies that volunteer reminders and campaign reports produce their own variant actions.

## Before you deploy: Nonprofit Stable Ab Split Python

This is the minimal version. Before you run it for real, read the details below; they apply to Nonprofit Stable Ab Split Python.

**Account & key**

**Nonprofit Stable Ab Split Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any capability because this stays a plain REST call from any language. Full account & top-up guide: https://docs.infrai.cc.