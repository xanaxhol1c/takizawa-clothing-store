import json
import hmac
import hashlib
import time
from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings

class PaymentStripeWebhookTestCase(TestCase):
    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_testsecret')
    def test_checkout_session_completed_webhook(self):
        payload = {
            "id": "evt_test_webhook",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_session",
                    "object": "checkout.session",
                    "mode": "payment",
                    "payment_status": "paid",
                    "payment_intent": "pi_test_123"
                }
            }
        }

        payload_str = json.dumps(payload)

        timestamp = str(int(time.time()))
        signed_payload = f'{timestamp}.{payload_str}'
        secret = settings.STRIPE_WEBHOOK_SECRET.encode('utf-8')
        signature = hmac.new(secret, signed_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        sig_header = f't={timestamp},v1={signature}'

        response = self.client.post(
            reverse('payments:webhook'),
            data=payload_str,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=sig_header
        )

        self.assertEqual(response.status_code, 200)

    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_testsecret')
    def test_checkout_session_webhook_signature_error(self):
        payload = {
            "id": "evt_test_webhook",
            "type": 123,
            "data": {
                "object": {
                    "id": "cs_test_session",
                    "object": "checkout.session",
                    "mode": 123,
                    "payment_status": 123,
                    "payment_intent": 123
                }
            }
        }

        payload_str = json.dumps(payload)

        timestamp = str(int(time.time()))
        signed_payload = f'{timestamp}.{payload_str}'
        secret = settings.STRIPE_WEBHOOK_SECRET.encode('utf-8')
        signature = hmac.new(secret, signed_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        sig_header = f't={timestamp},v1={signature}'

        response = self.client.post(
            reverse('payments:webhook'),
            data={},
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=sig_header
        )

        self.assertEqual(response.status_code, 400)

    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_testsecret')
    def test_checkout_session_webhook_value_error(self):
        payload_str = '{"incomplete_json": true'

        timestamp = str(int(time.time()))
        signed_payload = f'{timestamp}.{payload_str}'
        secret = settings.STRIPE_WEBHOOK_SECRET.encode('utf-8')
        signature = hmac.new(secret, signed_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        sig_header = f't={timestamp},v1={signature}'

        response = self.client.post(
            reverse('payments:webhook'),
            data=payload_str,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=sig_header
        )

        self.assertEqual(response.status_code, 400)
