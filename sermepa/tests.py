# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse
from django.test.client import Client
from django.test.utils import override_settings
from django.conf import settings

from sermepa.models import SermepaResponse, SermepaIdTPV
from sermepa.forms import SermepaPaymentForm
from sermepa.mixins import SermepaMixin


class SermepaModelTest(TestCase):

    @override_settings(SERMEPA_SECRET_KEY='qwertyasdf0123456789')
    def test_sermepa_response_creation(self):
        data = {
            'Ds_AuthorisationCode': '532895',
            'Ds_Date': '2011-12-12',
            'Ds_SecurePayment': 1,
            'Ds_MerchantData': 'custom_code',
            'Ds_Card_Country': 724,
            'Ds_Terminal': 1,
            'Ds_MerchantCode': '022711378',
            'Ds_ConsumerLanguage': 1,
            'Ds_Response': '0000',
            'Ds_Order': '1825926',
            'Ds_Currency': 978,
            'Ds_Amount': 25,
            'Ds_Signature': 'D381D30F295819A7129CE0D6E76EA228D9AA88C1',
            'Ds_TransactionType': '0',
            'Ds_Hour': '16:25',
        }
        response = SermepaResponse.objects.create(**data)
        self.assertIsNotNone(response.pk)
        self.assertEqual(response.Ds_Order, '1825926')

    def test_max_idtpv(self):
        new_idtpv = SermepaIdTPV.objects.new_idtpv()
        self.assertEqual(new_idtpv, '1000000001')
        new_idtpv = SermepaIdTPV.objects.new_idtpv()
        self.assertEqual(new_idtpv, '1000000002')

        SermepaIdTPV.objects.create(idtpv='2000100065')
        new_idtpv = SermepaIdTPV.objects.new_idtpv()
        self.assertEqual(new_idtpv, '2000100066')
        self.assertEqual(SermepaIdTPV.objects.filter(idtpv='2000100066').count(), 1)

    def test_sermepa_idtpv_str(self):
        idtpv = SermepaIdTPV.objects.create(idtpv='1234567890')
        self.assertEqual(str(idtpv), '1234567890')


class SermepaMixinTest(TestCase):

    def test_encode_decode_base64(self):
        mixin = SermepaMixin()
        original = b'test data'
        encoded = mixin.encode_base64(original)
        decoded = mixin.decode_base64(encoded)
        self.assertEqual(decoded, original)

    def test_urlsafe_encode_decode(self):
        mixin = SermepaMixin()
        original = b'test+data/with=special'
        encoded = mixin.urlsafe_b64encode(original)
        decoded = mixin.urlsafe_b64decode(encoded)
        self.assertEqual(decoded, original)

    @override_settings(SERMEPA_SECRET_KEY='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0')
    def test_firma_peticion(self):
        mixin = SermepaMixin()
        order = '1234567890'
        params = mixin.encode_base64(b'{"Ds_Merchant_Order":"1234567890"}')
        firma = mixin.get_firma_peticion(order, params, settings.SERMEPA_SECRET_KEY)
        self.assertIsInstance(firma, str)
        self.assertTrue(len(firma) > 0)

    def test_operacion_valida(self):
        self.assertTrue(SermepaMixin.operacion_valida('0'))
        self.assertTrue(SermepaMixin.operacion_valida('99'))
        self.assertFalse(SermepaMixin.operacion_valida('100'))
        self.assertFalse(SermepaMixin.operacion_valida('900'))


class SermepaFormTest(TestCase):

    @override_settings(
        SERMEPA_SECRET_KEY='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0',
        SERMEPA_TERMINAL='002',
        SERMEPA_MERCHANT_CODE='327234688',
        SERMEPA_CURRENCY='978',
        SERMEPA_SIGNATURE_VERSION='HMAC_SHA256_V1',
        SERMEPA_URL_PRO='https://sis.redsys.es/sis/realizarPago',
        SERMEPA_URL_TEST='https://sis-t.redsys.es:25443/sis/realizarPago',
    )
    def test_sermepa_payment_form_creation(self):
        merchant_parameters = {
            "Ds_Merchant_Titular": 'John Doe',
            "Ds_Merchant_MerchantData": '200010003000',
            "Ds_Merchant_MerchantName": 'Test Shop',
            "Ds_Merchant_ProductDescription": 'test',
            "Ds_Merchant_Amount": '200',
            "Ds_Merchant_TransactionType": '0',
            "Ds_Merchant_Terminal": settings.SERMEPA_TERMINAL,
            "Ds_Merchant_MerchantCode": settings.SERMEPA_MERCHANT_CODE,
            "Ds_Merchant_Order": '200010003000',
            "Ds_Merchant_Currency": settings.SERMEPA_CURRENCY,
            "Ds_Merchant_MerchantURL": 'http://localhost/sermepa/',
            "Ds_Merchant_UrlOK": 'http://localhost/end',
            "Ds_Merchant_UrlKO": 'http://localhost/end',
        }
        form = SermepaPaymentForm(merchant_parameters=merchant_parameters)
        self.assertIn('Ds_SignatureVersion', form.initial)
        self.assertIn('Ds_MerchantParameters', form.initial)
        self.assertIn('Ds_Signature', form.initial)

    @override_settings(
        SERMEPA_URL_PRO='https://sis.redsys.es/sis/realizarPago',
        SERMEPA_URL_TEST='https://sis-t.redsys.es:25443/sis/realizarPago',
    )
    def test_sermepa_form_render(self):
        form = SermepaPaymentForm()
        rendered = form.render_form()
        self.assertIn('form', rendered)
        self.assertIn('sis.redsys.es', rendered)

    @override_settings(
        SERMEPA_URL_TEST='https://sis-t.redsys.es:25443/sis/realizarPago',
    )
    def test_sermepa_form_sandbox(self):
        form = SermepaPaymentForm()
        rendered = form.sandbox()
        self.assertIn('sis-t.redsys.es', rendered)


class SermepaIPNTest(TestCase):

    @override_settings(SERMEPA_SECRET_KEY='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0')
    def test_ipn_url_resolves(self):
        url = reverse('sermepa_ipn')
        self.assertEqual(url, '/sermepa/')

    @override_settings(SERMEPA_SECRET_KEY='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0')
    def test_ipn_get_returns_200(self):
        c = Client()
        resp = c.post(reverse('sermepa_ipn'))
        self.assertEqual(resp.status_code, 200)


class SermepaSignalTest(TestCase):

    def test_signals_importable(self):
        from sermepa.signals import (
            payment_was_successful,
            payment_was_error,
            refund_was_successful,
            signature_error,
        )
        self.assertIsNotNone(payment_was_successful)
        self.assertIsNotNone(payment_was_error)
        self.assertIsNotNone(refund_was_successful)
        self.assertIsNotNone(signature_error)
