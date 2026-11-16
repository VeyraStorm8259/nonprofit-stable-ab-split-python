from nonprofit_split import choose_action


def test_variant_changes_donor_receipt_business_decision():
    assert choose_action("donor_receipt", "control") == "send_receipt_email"
    assert choose_action("donor_receipt", "variant") == "send_receipt_email_with_campaign_link"


def test_each_nonprofit_workflow_has_a_variant_action():
    assert choose_action("volunteer_reminder", "variant") == "send_reminder_email_with_shift_summary"
    assert choose_action("campaign_report", "variant") == "render_report_with_channel_breakdown"
