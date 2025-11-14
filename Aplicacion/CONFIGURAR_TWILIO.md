# 📱 Configuración de Notificaciones SMS con Twilio

## 🚀 Paso 1: Crear Cuenta en Twilio

1. Ve a: https://www.twilio.com/try-twilio
2. Regístrate con tu email (obtienes $15 USD gratis)
3. Verifica tu email y número de teléfono

## 🔑 Paso 2: Obtener Credenciales

1. Ve al **Dashboard de Twilio**: https://console.twilio.com
2. En la página principal verás:
   - **Account SID** (ejemplo: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (haz clic en "Show" para verlo)
3. **¡GUÁRDALOS!** Los necesitarás en el siguiente paso

## 📞 Paso 3: Obtener un Número Twilio

### Opción A: Número de Prueba (Trial - Gratis)
1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Twilio te asigna un número automáticamente (ejemplo: `+1234567890`)
3. **IMPORTANTE**: Con cuenta Trial solo puedes llamar/enviar SMS a **números verificados**

### Verificar el Número de Destino (+50662494299)
1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Haz clic en **"Add a new Caller ID"** o **"Verify a number"**
3. Ingresa: `+50662494299`
4. Twilio te llamará o enviará un código de verificación
5. Ingresa el código para verificar

### Opción B: Número Real (Después del Trial)
1. Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage/search
2. Busca un número disponible
3. Cómpralo (~$1-2 USD/mes)

## ⚙️ Paso 4: Configurar en tu Aplicación

Edita el archivo `config.py`:

```python
# Configuración de Twilio (SMS)
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Tu Account SID
TWILIO_AUTH_TOKEN = "tu_auth_token_de_32_caracteres"       # Tu Auth Token
TWILIO_PHONE_FROM = "+1234567890"                          # Tu número Twilio
TWILIO_PHONE_TO = "+50662494299"                           # Número de destino
```

## ✅ Paso 5: Probar la Configuración

Crea un archivo `test_twilio.py`:

```python
from notifications import TwilioNotifier

notifier = TwilioNotifier()

# Probar conexión
if notifier.test_connection():
    print("✓ Twilio configurado correctamente")
    
    # Enviar mensaje de prueba
    success = notifier.send_custom_message(
        "🧪 Prueba: Sistema de notificaciones funcionando"
    )
    
    if success:
        print("✓ SMS enviado exitosamente")
    else:
        print("✗ Error al enviar SMS")
else:
    print("✗ Error de configuración")
```

Ejecuta:
```bash
python test_twilio.py
```

## 💰 Costos Estimados

### Cuenta Trial (Gratis)
- **Crédito**: $15 USD
- **Limitaciones**: Solo números verificados
- **SMS a Costa Rica**: ~$0.02 USD por mensaje

### Cuenta de Producción
- **Número Twilio**: ~$1-2 USD/mes
- **SMS a Costa Rica**: ~$0.015-0.02 USD por mensaje
- **Sin verificaciones**: Puedes enviar a cualquier número

## 🔐 Seguridad

**NUNCA** compartas tus credenciales:
- No las subas a GitHub
- No las compartas en Discord/WhatsApp
- Considera usar variables de entorno:

```python
import os
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "default_value")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "default_value")
```

## 🆘 Solución de Problemas

### Error: "Unable to create record"
- Verifica que el número de destino esté verificado (si usas Trial)
- Asegúrate de incluir el código de país: `+506`

### Error: "Authenticate"
- Verifica tu Account SID y Auth Token
- Copia y pega sin espacios extras

### Error: "From phone number"
- Verifica que tu número Twilio esté activo
- Formato correcto: `+1234567890`

### El SMS no llega
- Revisa el estado en: https://console.twilio.com/us1/monitor/logs/sms
- Verifica que el número esté en formato internacional

## 📚 Documentación Oficial

- **Twilio Docs**: https://www.twilio.com/docs/sms
- **Python SDK**: https://www.twilio.com/docs/libraries/python
- **Precios SMS**: https://www.twilio.com/en-us/sms/pricing

## 🎯 Funcionalidad en tu Proyecto

Una vez configurado, el sistema:
1. ✅ Detecta cuando el ESP32 envía "Colisión detectada"
2. ✅ Detiene el carrito automáticamente
3. ✅ Envía SMS a +50662494299 con la alerta
4. ✅ Muestra notificación en la GUI
5. ✅ Registra el evento en el log

**Cooldown**: 10 segundos entre notificaciones (configurable en `config.py`)
