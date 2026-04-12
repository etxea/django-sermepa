==============
django-sermepa
==============

Django sermepa es una aplicación muy al estilo de django-paypal para usar el TPV Virtual de Redsys/Sermepa, el TPV más usado en España.

Permite generar cobros puntuales, recurrentes por fichero o por referencia, y devoluciones.

La app tiene una vista que escucha las notificaciones del TPV (se debe pedir su activación a tu banco) y lanza signals para que sean procesadas por tu aplicación de cobros, para cambiar de estado el pedido, enviar emails de notificación...

**Este fork implementa la versión 2.1 de Sermepa (SHA-256).**

Versiones compatibles
---------------------

- Python: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Django: 3.2, 4.0, 4.1, 4.2, 5.0, 5.1

Historial de versiones
----------------------

- **2.0.0**: Soporte para Django 3.2 a 5.1 y Python 3.8 a 3.13. CI con GitHub Actions. Ver `CHANGELOG.md <CHANGELOG.md>`_ para el detalle completo de cambios.
- 1.1.5: Corrección de errores en form y mixin. Django 2.2 y Python 3.8.
- 1.1.4: Corrección de errores de empaquetado, migraciones y readme. Django 1.11 y Python 3.6.
- 1.1.3: Soporte django 1.4+ (probado en 1.4, 1.5, 1.6, 1.7).
- 1.1.2: Compatible con python 2.7 y python 3.x.

Instalación
-----------

1. Instala el proyecto usando pip::

    pip install django-sermepa

   O directamente desde GitHub::

    pip install git+https://github.com/Etxea/django-sermepa

2. Añádelo a INSTALLED_APPS del settings.py:

 .. code:: python

    INSTALLED_APPS += ('sermepa',)
 ..

3. Aplica migraciones::

    python manage.py migrate

Configuración
-------------

4. Añade los siguientes settings:

 .. code:: python

    SERMEPA_URL_PRO = 'https://sis.redsys.es/sis/realizarPago'
    SERMEPA_URL_TEST = 'https://sis-t.redsys.es:25443/sis/realizarPago'
    SERMEPA_MERCHANT_CODE = '327234688'  # comercio de test
    SERMEPA_TERMINAL = '002'
    SERMEPA_SECRET_KEY = 'tu_clave_secreta_en_base64'
    SERMEPA_CURRENCY = '978'  # Euros
    SERMEPA_SIGNATURE_VERSION = 'HMAC_SHA256_V1'
 ..

 Deberás modificar SERMEPA_MERCHANT_CODE, SERMEPA_SECRET_KEY, SERMEPA_TERMINAL con los datos proporcionados por tu banco.

5. Añade la ruta de la respuesta de Sermepa a tus urls:

 .. code:: python

    from django.urls import include, path

    urlpatterns = [
        path('sermepa/', include('sermepa.urls')),
        # ...
    ]
 ..

Uso
---

6. Programa los listeners de las signals de OK, KO y si quieres de error:

 6.1 El listener recibe un objeto de tipo `SermepaResponse <https://github.com/Etxea/django-sermepa/blob/main/sermepa/models.py>`_
 con toda la información de la operación del TPV. Puedes usar un listener que procese todos los casos, o uno por cada caso (OK y KO):

 .. code:: python

    def payment_ok(sender, **kwargs):
        '''sender es un objeto de clase SermepaResponse. Utiliza el campo Ds_MerchantData
        para asociarlo a tu Pedido o Carrito'''
        pedido = Pedido.objects.get(id=sender.Ds_MerchantData)
        pedido.estado = 'cobrado'
        pedido.Ds_AuthorisationCode = sender.Ds_AuthorisationCode
        pedido.save()
        send_email_success(pedido)

    def payment_ko(sender, **kwargs):
        '''sender es un objeto de clase SermepaResponse'''
        pass

    def sermepa_ipn_error(sender, **kwargs):
        '''Esta señal salta cuando el POST data recibido está mal firmado.'''
        pass
 ..

 6.2 Asocia el listener a las señales, en algún punto que se cargue al iniciar el proyecto, por ejemplo en el models.py:

 .. code:: python

    from sermepa.signals import payment_was_successful
    from sermepa.signals import payment_was_error
    from sermepa.signals import signature_error

    payment_was_successful.connect(payment_ok)
    payment_was_error.connect(payment_ko)
    signature_error.connect(sermepa_ipn_error)
 ..


7. Utiliza el form de `SermepaPaymentForm <https://github.com/Etxea/django-sermepa/blob/main/sermepa/forms.py>`_ para inicializar el botón de pago.

 El botón de pago será un formulario POST a la url del TPV, firmado con tu clave secreta, que deberá pasar toda la información de la operación: modalidad de pago, importe (en céntimos), URLs de notificación, OK y KO, descripción, datos del comercio, identificador de tu pedido, identificador de la operación...

 Existen diferentes modalidades de pago:

 1. Las compras puntuales, el Ds_Merchant_TransactionType='0' y el Ds_Merchant_Order debe ser un string siempre único y de 10 caracteres.

 2. Las suscripciones o pagos recurrentes. Existen 2 tipos, por fichero o por referencia.

  2.1 Por fichero, tienen un límite de 12 meses o 12 cobros.

   2.1.1 El primer cobro el Ds_Merchant_TransactionType='L' y el Ds_Merchant_Order debe ser siempre único.

    El tpv responde con el mismo valor pasado en la variable Ds_Order más 2 dígitos adicionales indicando el número de transacción (la primera es 00)

   2.1.2 Los cobros sucesivos se debe pasar el Ds_Merchant_TransactionType='M' y el primer Ds_Merchant_Order

  2.2 Por referencia, no tiene límite de tiempo ni de cobros. Este sistema soporta cobros de 0€ para activaciones y cambios de tarjetas.

   2.2.1 El primer cobro el Ds_Merchant_TransactionType='0' y el Ds_Merchant_Order='REQUIRED'

    El tpv responde con un nuevo parámetro Ds_Merchant_Identifier, que hay que almacenar (idreferencia)

   2.2.2 Los cobros sucesivos son Ds_Merchant_TransactionType='0' y el Ds_Merchant_Order=idreferencia (el valor que nos han pasado en el primero cobro)

 **Mira el código del ejemplo** (`sermepa_test/views.py <https://github.com/Etxea/django-sermepa/blob/main/sermepa_test/views.py>`_) para más info:

  .. code:: python

    from django.shortcuts import render
    from django.urls import reverse
    from sermepa.forms import SermepaPaymentForm
    from sermepa.models import SermepaIdTPV

    def form(request, trans_type='0'):
        site = Site.objects.get_current()
        amount = int(5.50 * 100)  # El precio es en céntimos de euro

        sermepa_dict = {
            "Ds_Merchant_Titular": 'John Doe',
            "Ds_Merchant_MerchantData": 12345,
            "Ds_Merchant_MerchantName": 'ACME',
            "Ds_Merchant_ProductDescription": 'petardos',
            "Ds_Merchant_Amount": amount,
            "Ds_Merchant_Terminal": settings.SERMEPA_TERMINAL,
            "Ds_Merchant_MerchantCode": settings.SERMEPA_MERCHANT_CODE,
            "Ds_Merchant_Currency": settings.SERMEPA_CURRENCY,
            "Ds_Merchant_MerchantURL": "http://%s%s" % (site.domain, reverse('sermepa_ipn')),
            "Ds_Merchant_UrlOK": "http://%s%s" % (site.domain, reverse('end')),
            "Ds_Merchant_UrlKO": "http://%s%s" % (site.domain, reverse('end')),
            "Ds_Merchant_Order": SermepaIdTPV.objects.new_idtpv(),
            "Ds_Merchant_TransactionType": '0',
        }
        form = SermepaPaymentForm(merchant_parameters=sermepa_dict)

        return render(request, 'form.html', {'form': form, 'debug': settings.DEBUG})

  ..

  y el form.html:

    .. code:: html

        <html>
        <body>
            {% if debug %}
                {{ form.sandbox }}
            {% else %}
                {{ form.render_form }}
            {% endif %}
        </body>
        </html>

  ..

8. El TPV enviará una respuesta (SermepaResponse) con la información que se le ha enviado más nuevos datos relacionados con el pago. A destacar:

 - Ds_MerchantData es el mismo valor enviado en el formulario en el campo Ds_Merchant_MerchantData. Debería contener el identificador de tu Pedido o Carrito
 - Ds_Merchant_Identifier: la referencia para cobros recurrentes sucesivos si se utiliza el pago por referencia.
 - Ds_ExpiryDate: Fecha de expiración de la tarjeta
 - Ds_Card_Number: Número asteriscado de la tarjeta
 - Ds_AuthorisationCode: Código de la operación autorizada, para poder hacer una devolución posterior.


9. Prueba el formulario de compra puntual en http://localhost:8000/ o http://localhost:8000/L/ ...

Desarrollo
----------

Ejecutar tests::

    pip install pytest pytest-django
    DJANGO_SETTINGS_MODULE=settings pytest sermepa/tests.py -v

Ejecutar tests en múltiples versiones con tox::

    pip install tox
    tox

Licencia
--------

MIT License
