-- Миграция: Добавление таблицы настроек компании
-- Дата: 2025-08-03

CREATE TABLE IF NOT EXISTS company_settings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    website VARCHAR(500),
    email VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    telegram_accounts JSON,
    ai_providers JSON,
    default_settings JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание триггера для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_company_settings_updated_at 
    BEFORE UPDATE ON company_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Вставка дефолтных настроек компании
INSERT INTO company_settings (
    name, 
    description, 
    telegram_accounts, 
    ai_providers, 
    default_settings
) VALUES (
    'Моя компания',
    'Настройки компании для Telegram Claude Agent',
    '[]'::json,
    '{
        "openai": {"enabled": false, "default_model": "gpt-4"},
        "claude": {"enabled": false, "default_agent": ""}
    }'::json,
    '{
        "context_messages_count": 3,
        "response_delay": 1.0,
        "auto_reply": true,
        "work_hours_enabled": false,
        "work_start": "09:00",
        "work_end": "18:00"
    }'::json
) ON CONFLICT DO NOTHING;