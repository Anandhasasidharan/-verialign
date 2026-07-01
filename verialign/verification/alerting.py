import logging

from verialign.verification.models import VerificationResult

logger = logging.getLogger(__name__)


async def send_alert(
    webhook_url: str | None,
    slack_webhook_url: str | None,
    text: str,
    result: VerificationResult,
) -> None:
    if not webhook_url and not slack_webhook_url:
        return

    summary = result.summary
    if summary["unsupported"] == 0 and summary["contradictions_found"] == 0:
        return

    payload = {
        "text": f"VeriAlign Alert\n\nText: {text[:500]}...\nUnsupported: {summary['unsupported']}\nContradictions: {summary['contradictions_found']}",
        "claims": [c.to_dict() for c in result.claims],
        "contradictions": [c.to_dict() for c in result.contradictions],
        "summary": summary,
    }

    import httpx

    async with httpx.AsyncClient() as client:
        if slack_webhook_url:
            try:
                slack_payload = {"text": payload["text"]}
                await client.post(slack_webhook_url, json=slack_payload, timeout=10)
            except Exception:
                logger.exception("slack_alert_failed")
        if webhook_url:
            try:
                await client.post(webhook_url, json=payload, timeout=10)
            except Exception:
                logger.exception("webhook_alert_failed")
