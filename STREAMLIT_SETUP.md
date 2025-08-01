# Настройка Streamlit Cloud для подключения к DigitalOcean Backend

## Backend успешно развернут! 🎉

**URL Backend API**: https://answerbot-magph.ondigitalocean.app

### Настройка Streamlit Cloud

1. Перейдите в настройки вашего Streamlit Cloud приложения
2. В разделе "Secrets" добавьте следующую конфигурацию:

```toml
# Backend API URL - DigitalOcean App Platform
BACKEND_API_URL = "https://answerbot-magph.ondigitalocean.app"

[general]
environment = "production"
```

### Проверка работы

После добавления secrets:
1. Перезапустите Streamlit приложение
2. Проверьте, что статус backend показывает "🟢 healthy"
3. База данных должна показывать "🟢 Подключена"
4. Telegram будет показывать "🔴 Отключен" (это нормально для минимального режима)

### API Endpoints

- **Health Check**: https://answerbot-magph.ondigitalocean.app/health
- **API Documentation**: https://answerbot-magph.ondigitalocean.app/docs
- **Campaigns**: https://answerbot-magph.ondigitalocean.app/api/campaigns/

### Конфигурация системы

- ✅ **OpenAI только**: Claude отключен, используется только OpenAI API
- ✅ **База данных**: SQLite подключена и работает
- ✅ **Минимальный режим**: Backend работает без Telegram интеграции
- ✅ **CORS**: Настроен для работы со Streamlit Cloud

Система готова к работе! 🚀